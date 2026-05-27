from ucumvert import PintUcumRegistry

ureg = PintUcumRegistry()


def is_valid_ucum(unit_code: str) -> bool:
    try:
        ureg.from_ucum(unit_code)
        return True
    except Exception:
        return False