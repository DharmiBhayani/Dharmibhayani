from database.database import save_ai_log


def log_request(
    project_id,
    agent,
    model,
    input_text,
    output_text,
    input_tokens=0,
    output_tokens=0,
    total_tokens=0,
    latency=0.0,
    cost=0.0,
    source_pages=None
):

    save_ai_log(
        project_id=project_id,
        agent=agent,
        model=model,
        input_text=input_text,
        output_text=output_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        tokens=total_tokens,
        latency=latency,
        cost=cost
    )