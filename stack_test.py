import yaml
import subprocess
import sys
import re

def maxima(expr):
    """Evaluate an expression in Maxima."""
    p = subprocess.run(
        ["maxima", "--very-quiet"],
        input=f"print({expr});",
        text=True,
        capture_output=True
    )
    
    lines = p.stdout.splitlines()

    # Ladehinweise entfernen (;;; Loading ...)
    clean = [ln for ln in lines if not ln.strip().startswith(";;;")]

    # Letzte sinnvolle Zeile ist das Ergebnis
    return clean[-1].strip() if clean else ""


def parse_variables(block):
    """Parse Maxima variable definitions from questionvariables."""
    assignments = {}
    lines = block.split(";")
    for line in lines:
        if ":" in line:
            name, expr = line.split(":", 1)
            name = name.strip()
            expr = expr.strip()
            value = maxima(expr)
            assignments[name] = value
    return assignments

def substitute(expr, variables):
    """Replace variable names in student answers."""
    for k, v in variables.items():
        expr = re.sub(rf"\b{k}\b", v, expr)
    return expr

def run_stack_test(yaml_file):
    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print(f"=== Test: {data['title']} ===")

    # 1. Variablen aus questionvariables
    variables = parse_variables(data["questionvariables"])
    print("Variablen:", variables)

    # 2. Testfälle
    for tc in data["test_cases"]:
        print(f"\nTestfall: {tc['name']}")

        student_ans = tc["studentanswers"]["ans1"]
        substituted = substitute(student_ans, variables)
        print("Schülerantwort (eingesetzt):", substituted)

        # Erwartete Lösung aus Maxima
        sol = variables["sol"]
        print("Erwartete Lösung:", sol)

        # Vergleich
        result = maxima(f"is(equal({substituted}, {sol}))")
        print("Maxima-Vergleich:", result)

        # Bewertung
        if result == "true":
            score = 1.0
        else:
            score = 0.0

        print("Berechneter Score:", score)
        print("Erwarteter Score:", tc["expected_score"])

        if score == tc["expected_score"]:
            print("✔ Score korrekt")
        else:
            print("✘ Score falsch")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bitte YAML-Datei angeben.")
        sys.exit(1)

    run_stack_test(sys.argv[1])
