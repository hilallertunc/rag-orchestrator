from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.request_log import RequestLog

async def get_metrics(db: AsyncSession) -> dict:
    total = await db.scalar(select(func.count()).select_from(RequestLog))
    
    strategy_rows = await db.execute(
        select(RequestLog.strategy, func.count().label("count"))
        .group_by(RequestLog.strategy)
    )
    strategy_dist = {row.strategy: row.count for row in strategy_rows}

    avg_duration = await db.scalar(select(func.avg(RequestLog.duration_ms)))
    avg_tokens = await db.scalar(select(func.avg(RequestLog.tokens_used)))
    total_tokens = await db.scalar(select(func.sum(RequestLog.tokens_used)))

    cache_hits = strategy_dist.get("cache_hit", 0)
    cache_hit_rate = round((cache_hits / total) * 100, 2) if total else 0

    model_rows = await db.execute(
        select(RequestLog.model, func.count().label("count"))
        .group_by(RequestLog.model)
    )
    model_dist = {row.model: row.count for row in model_rows}

    return {
        "total_requests": total,
        "cache_hit_rate_percent": cache_hit_rate,
        "strategy_distribution": strategy_dist,
        "model_distribution": model_dist,
        "avg_duration_ms": round(avg_duration or 0, 2),
        "avg_tokens_used": round(avg_tokens or 0, 2),
        "total_tokens_used": total_tokens or 0,
    }