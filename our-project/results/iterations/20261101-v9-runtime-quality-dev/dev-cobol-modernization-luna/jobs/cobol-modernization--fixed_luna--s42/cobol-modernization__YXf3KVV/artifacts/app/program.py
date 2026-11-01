from pathlib import Path

ROOT = Path('/app')
DATA = ROOT / 'data'


def read_record(handle, size):
    record = handle.read(size)
    if not record:
        return None
    if len(record) != size:
        # Sequential fixed-width records are not padded by COBOL; a partial trailing
        # record is nevertheless read as bytes and subsequent fields are spaces.
        record = record.ljust(size, b' ')
    return record


def main():
    input_path = ROOT / 'src' / 'INPUT.DAT'
    with input_path.open('rb') as f:
        raw = f.read(32)
    if not raw:
        print('Error: Input file is empty')
        return
    raw = raw.ljust(32, b' ')
    buyer, seller, book, amount_raw = raw[:4], raw[4:8], raw[8:12], raw[12:22]
    try:
        amount = int(amount_raw)
    except ValueError:
        # Numeric input is expected to be valid PIC 9(10), as it is in COBOL.
        amount = 0
    cents = amount

    accounts_path = DATA / 'ACCOUNTS.DAT'
    books_path = DATA / 'BOOKS.DAT'
    transactions_path = DATA / 'TRANSACTIONS.DAT'

    buyer_found = seller_found = book_found = valid_owner = False
    with accounts_path.open('rb') as f:
        while True:
            r = read_record(f, 34)
            if r is None:
                break
            account_id = r[:4]
            buyer_found |= account_id == buyer
            seller_found |= account_id == seller
    with books_path.open('rb') as f:
        while True:
            r = read_record(f, 28)
            if r is None:
                break
            if r[:4] == book:
                book_found = True
                if r[24:28] == seller:
                    valid_owner = True

    print(' ')
    if not (buyer_found and seller_found and book_found and valid_owner):
        print('Transaction failed due to validation errors')
        return

    # Sequential COBOL files contain concatenated fixed-length records. REWRITE
    # updates each matching record in place; duplicate IDs are all updated.
    original = accounts_path.read_bytes()
    updated = bytearray()
    for pos in range(0, len(original), 34):
        r = original[pos:pos + 34].ljust(34, b' ')
        aid = r[:4]
        if aid == buyer or aid == seller:
            try:
                balance = int(r[24:34])
            except ValueError:
                balance = 0
            # COBOL runs the buyer SUBTRACT then seller ADD tests independently.
            if aid == buyer:
                balance = (balance - cents) % 10_000_000_000
            if aid == seller:
                balance = (balance + cents) % 10_000_000_000
            r = r[:24] + f'{balance:010d}'.encode('ascii')
        updated.extend(r)
    accounts_path.write_bytes(updated)

    original = books_path.read_bytes()
    updated = bytearray()
    for pos in range(0, len(original), 28):
        r = original[pos:pos + 28].ljust(28, b' ')
        if r[:4] == book:
            r = r[:24] + buyer
        updated.extend(r)
    books_path.write_bytes(updated)

    # OPEN EXTEND and WRITE append a fixed-width transaction record.
    with transactions_path.open('ab') as f:
        f.write(book + f'{cents:010d}'.encode('ascii') + seller + buyer)
    print('Transaction completed successfully')


if __name__ == '__main__':
    main()
