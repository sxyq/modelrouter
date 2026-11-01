#!/usr/bin/env python3
"""Byte-for-byte Python implementation of src/program.cbl (GnuCOBOL 3).

The COBOL files are SEQUENTIAL, not LINE SEQUENTIAL: records have fixed
byte widths and there are no line separators or record headers.
"""

import os
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent
BALANCE_MODULUS = 10 ** 10
UINT64_MASK = (1 << 64) - 1


class CobolFileError(Exception):
    """An unhandled COBOL file status stops the program, without rollback."""

    def __init__(self, name, relative_path, status, message, opened=False):
        self.name = name
        self.relative_path = relative_path
        self.status = status
        self.message = message
        self.opened = opened
        super().__init__(message)

    def report(self):
        directory = self.relative_path.split('/')[0]
        print(
            f"libcob: error: {self.message} (status = {self.status:02d}) "
            f"for file {self.name} ('{directory}' => {self.relative_path})",
            file=sys.stderr,
        )
        if self.opened:
            print(
                f"libcob: warning: implicit CLOSE of {self.name} "
                f"('{self.relative_path}')",
                file=sys.stderr,
            )


class SequentialFile:
    """A fixed-size FD buffer persists through short reads and CLOSE/OPEN."""

    def __init__(self, name, relative_path, size):
        self.name = name
        self.relative_path = relative_path
        self.path = BASE_DIR / relative_path
        self.size = size
        # GnuCOBOL's file-section storage starts as binary zeroes.
        self.record = bytearray(size)
        self.stream = None
        self.read_done = False

    def fail(self, status, message):
        raise CobolFileError(
            self.name, self.relative_path, status, message,
            opened=self.stream is not None,
        )

    def open(self, mode):
        try:
            if mode == 'extend':
                # OPEN EXTEND on this non-OPTIONAL file must not create it.
                fd = os.open(self.path, os.O_WRONLY | os.O_APPEND)
                self.stream = os.fdopen(fd, 'wb', buffering=0)
            else:
                self.stream = self.path.open(mode, buffering=0)
        except FileNotFoundError:
            self.fail(35, 'file does not exist')
        except PermissionError:
            self.fail(37, 'permission denied')
        except OSError:
            self.fail(30, 'permanent file error')
        self.read_done = False
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self.stream is not None:
            self.stream.close()
            self.stream = None

    def read(self):
        try:
            data = self.stream.read(self.size)
        except OSError:
            self.fail(30, 'permanent file error')
        self.read_done = len(data) == self.size
        if not data:
            return False
        # A short read is processed, but the unread tail remains unchanged.
        self.record[:len(data)] = data
        return True

    def rewrite(self):
        if not self.read_done:
            self.fail(43, 'READ must be executed first')
        try:
            self.stream.seek(-self.size, os.SEEK_CUR)
            self.stream.write(self.record)
        except OSError:
            self.fail(30, 'permanent file error')
        # A second REWRITE without another full READ is status 43.
        self.read_done = False

    def write(self, record):
        try:
            self.stream.write(record)
        except OSError:
            self.fail(30, 'permanent file error')


def display_number(data):
    """GnuCOBOL's unsigned numeric-display to decimal conversion.

    Leading bytes with a zero low nibble are skipped. The remaining ASCII
    digit conversion uses an unsigned 64-bit accumulator. This intentionally
    does not reject nonnumeric bytes, just as the original does not.
    """
    if data == b'\xff' * len(data):
        return 10 ** len(data) - 1
    if data == b'\x00' * len(data):
        return 0
    start = 0
    while start < len(data) - 1 and data[start] & 0x0F == 0:
        start += 1
    value = 0
    for byte in data[start:]:
        value = (value * 10 + byte - ord('0')) & UINT64_MASK
    return value


def balance_bytes(value):
    # Unsigned PIC 9(10) discards the sign and excess high-order digits.
    return f'{abs(value) % BALANCE_MODULUS:010d}'.encode('ascii')


def main():
    inputs = SequentialFile('INPUT-FILE', 'src/INPUT.DAT', 22)
    accounts = SequentialFile('ACCOUNTS-FILE', 'data/ACCOUNTS.DAT', 34)
    books = SequentialFile('BOOKS-FILE', 'data/BOOKS.DAT', 28)
    transactions = SequentialFile(
        'TRANSACTIONS-FILE', 'data/TRANSACTIONS.DAT', 22,
    )

    with inputs.open('rb'):
        if not inputs.read():
            print('Error: Input file is empty')
            print(
                "libcob: warning: implicit CLOSE of INPUT-FILE ('src/INPUT.DAT')",
                file=sys.stderr,
            )
            return 0
        buyer = bytes(inputs.record[:4])
        seller = bytes(inputs.record[4:8])
        book_id = bytes(inputs.record[8:12])
        # MOVE PIC 9(10) to PIC 9(10)V99 copies the integer digits and adds
        # two fractional zeroes. Spaces and binary zeroes become ASCII zeroes.
        amount_digits = bytes(inputs.record[12:22]).translate(
            bytes.maketrans(b'\x00 ', b'00')
        )
        amount_scaled = display_number(amount_digits + b'00')

    buyer_found = seller_found = False
    with accounts.open('rb'):
        while accounts.read():
            account_id = bytes(accounts.record[:4])
            if account_id == buyer:
                buyer_found = True
            if account_id == seller:
                seller_found = True

    book_found = valid_owner = False
    with books.open('rb'):
        while books.read():
            if books.record[:4] == book_id:
                book_found = True
                if books.record[24:28] == seller:
                    valid_owner = True
    print(' ')

    if not (buyer_found and seller_found and book_found and valid_owner):
        print('Transaction failed due to validation errors')
        return 0

    with accounts.open('r+b'):
        while accounts.read():
            if accounts.record[:4] == buyer:
                balance = display_number(bytes(accounts.record[24:34]))
                # Arithmetic aligns the balance with WS-AMOUNT's two decimal
                # places. Truncate fractional digits after taking magnitude.
                result = abs(balance * 100 - amount_scaled) // 100
                accounts.record[24:34] = balance_bytes(result)
                accounts.rewrite()
            if accounts.record[:4] == seller:
                balance = display_number(bytes(accounts.record[24:34]))
                result = (balance * 100 + amount_scaled) // 100
                accounts.record[24:34] = balance_bytes(result)
                accounts.rewrite()

    with books.open('r+b'):
        while books.read():
            if books.record[:4] == book_id:
                books.record[24:28] = buyer
                books.rewrite()

    with transactions.open('extend'):
        # MOVE back to PIC 9(10) preserves the original integer digit bytes.
        transactions.write(book_id + amount_digits + seller + buyer)
    print('Transaction completed successfully')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except CobolFileError as error:
        error.report()
        sys.exit(1)
