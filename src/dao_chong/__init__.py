"""道冲模型检索层（L2）——把 dao-chong-schema.json 变成可查询能力。"""

from .ontology import Ontology, normalize_pinyin, SCHEMA_PATH

__all__ = ["Ontology", "normalize_pinyin", "SCHEMA_PATH"]

__version__ = "0.1.0"
