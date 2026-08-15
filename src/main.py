from src.validator.uetr import is_valid_uetr


def main() -> None:
    print("=" * 64)
    print("SWIFT GPI UETR PAYMENT TRACKER")
    print("Validation & Workflow Utility")
    print("=" * 64)

    print()
    print("Environment : Authorized Development / Testing")
    print("Mode        : Local Validation")
    print()

    example_uetr = (
        "550e8400-e29b-41d4-a716-446655440000"
    )

    result = is_valid_uetr(example_uetr)

    print(f"UETR        : {example_uetr}")
    print(f"Validation  : {'VALID' if result else 'INVALID'}")

    print()
    print("System ready.")
    print("=" * 64)


if __name__ == "__main__":
    main()
