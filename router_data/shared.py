"""Internal shared implementation for prepare_router_data.py."""

import json


def write_json(path, data):
    """Write reports with the existing UTF-8 formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_jsonl(path, records):
    """Write records in order without collecting an iterable in memory."""
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class StreamingFieldTracker:
    """
    流式全量字段缺失率统计器：
    - 伴随全量清洗产物写入进行流式累计 (O(1) 内存开销)
    - 覆盖 100% 真实清洗行数 (针对数百万条记录做真实扫描)
    - 严格识别 None、空字符串与 'unknown' 为缺失
    """
    def __init__(self, schema_template):
        self.schema_template = schema_template
        self.total_count = 0
        self.missing_counts = {}
        for fpath, fval in schema_template.items():
            if not (isinstance(fval, dict) and "value" in fval):
                self.missing_counts[fpath] = 0

    def update(self, record):
        self.total_count += 1
        for fpath in self.missing_counts:
            curr = record
            for part in fpath.split("."):
                if isinstance(curr, dict) and part in curr:
                    curr = curr[part]
                else:
                    curr = None
                    break
            if curr is None or curr == "" or curr == "unknown":
                self.missing_counts[fpath] += 1

    def build_schema(self):
        res = {}
        denom = max(1, self.total_count)
        for fpath, fval in self.schema_template.items():
            if isinstance(fval, dict) and "value" in fval:
                res[fpath] = fval
            else:
                m_count = self.missing_counts.get(fpath, 0)
                m_rate = round(m_count / denom, 4)
                res[fpath] = {
                    "type": fval,
                    "missing_rate": m_rate,
                    "total_scanned": self.total_count,
                    "missing_count": m_count,
                }
        return res
