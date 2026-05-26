def attempt_with_repair(action_func, repair_func, max_attempts=3):
    for attempt in range(max_attempts):
        response = action_func()

        if response.status_code in [200, 201, 204]:
            return response

        error_data = response.json()
        fix_payload = repair_func(error_data)

        if not fix_payload:
            break

        repair_func.apply_fix(fix_payload)

    return response