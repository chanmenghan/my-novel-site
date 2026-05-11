"""API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import csv
import io
import uuid
from pathlib import Path

from config import DATA_DIR

router = APIRouter()

sessions: Dict[str, Dict[str, Any]] = {}


class ColumnInfo(BaseModel):
    name: str
    type: str
    unique_count: int
    sample_values: List[str]


class ChartConfig(BaseModel):
    type: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    title: str = ""


class CSVDataResponse(BaseModel):
    session_id: str
    filename: str
    row_count: int
    column_count: int
    columns: List[ColumnInfo]
    data: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "csv-viewer"}


@router.post("/upload", response_model=CSVDataResponse)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="只支持 CSV 文件")

    content = await file.read()

    try:
        decoded_content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            decoded_content = content.decode('gbk')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="文件编码不支持，请使用 UTF-8 或 GBK 编码")

    reader = csv.DictReader(io.StringIO(decoded_content))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV 文件为空")

    fieldnames = reader.fieldnames or []
    columns = []
    for name in fieldnames:
        values = [str(row.get(name, '')) for row in rows[:100] if row.get(name)]
        unique_values = set(values)
        is_numeric = all(v.replace('.', '').replace('-', '').isdigit() or v == '' for v in values[:50])

        columns.append(ColumnInfo(
            name=name,
            type="number" if is_numeric else "text",
            unique_count=len(unique_values),
            sample_values=list(unique_values)[:5]
        ))

    numeric_columns = [c.name for c in columns if c.type == "number"]

    charts = []
    if numeric_columns:
        charts.append({
            "type": "bar",
            "x_axis": fieldnames[0] if fieldnames else "",
            "y_axis": numeric_columns[0] if numeric_columns else "",
            "title": f"{numeric_columns[0]} 分布"
        })

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "filename": file.filename,
        "data": rows,
        "columns": columns,
        "numeric_columns": numeric_columns
    }

    return CSVDataResponse(
        session_id=session_id,
        filename=file.filename,
        row_count=len(rows),
        column_count=len(fieldnames),
        columns=columns,
        data=rows[:500],
        charts=charts
    )


@router.get("/data/{session_id}")
async def get_csv_data(session_id: str, page: int = 1, page_size: int = 100):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")

    session = sessions[session_id]
    rows = session["data"]

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "session_id": session_id,
        "filename": session["filename"],
        "row_count": len(rows),
        "page": page,
        "page_size": page_size,
        "data": rows[start:end]
    }


@router.get("/charts/{session_id}")
async def get_chart_data(session_id: str, chart_type: str = "bar"):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")

    session = sessions[session_id]
    rows = session["data"]
    columns = session["columns"]
    numeric_columns = session["numeric_columns"]

    if chart_type == "bar" and numeric_columns:
        x_col = columns[0].name
        y_col = numeric_columns[0]

        labels = [str(row.get(x_col, ''))[:20] for row in rows[:50]]
        values = []
        for row in rows[:50]:
            try:
                val = float(row.get(y_col, 0))
            except (ValueError, TypeError):
                val = 0
            values.append(val)

        return {
            "type": "bar",
            "title": f"{y_col} 统计",
            "labels": labels,
            "datasets": [{
                "label": y_col,
                "data": values
            }]
        }

    elif chart_type == "line" and numeric_columns:
        y_col = numeric_columns[0]
        labels = [str(i + 1) for i in range(len(rows[:100]))]
        values = []
        for row in rows[:100]:
            try:
                val = float(row.get(y_col, 0))
            except (ValueError, TypeError):
                val = 0
            values.append(val)

        return {
            "type": "line",
            "title": f"{y_col} 趋势",
            "labels": labels,
            "datasets": [{
                "label": y_col,
                "data": values
            }]
        }

    return {"type": "unknown", "message": "不支持的图表类型"}