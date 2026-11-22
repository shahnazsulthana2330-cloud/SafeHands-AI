# SAFEHANDS AI - JOB SCAM CHECKER

def check_job(job_description):

    warning_signals = {
        "registration fee": 20,
        "joining fee": 20,
        "processing fee": 20,
        "pay money": 20,
        "guaranteed job": 15,
        "no interview": 15,
        "urgent hiring": 10,
        "limited vacancies": 10
    }

    found_signals = []
    risk_score = 0

    job_description = job_description.lower()

    for signal, points in warning_signals.items():

        if signal in job_description:
            found_signals.append(signal)
            risk_score += points

    risk_score = min(risk_score, 100)

    print("\n===== SAFEHANDS AI REPORT =====")
    print("Risk Score:", risk_score, "/ 100")

    if risk_score >= 60:
        print("Risk Level: HIGH")
    elif risk_score >= 20:
        print("Risk Level: MEDIUM")
    else:
        print("Risk Level: LOW")

    print("\nWarning Signals Found:")

    if found_signals:
        for signal in found_signals:
            print("-", signal)
    else:
        print("No listed warning signals found.")

    print("\nPlease verify the company before applying.")
    print("This is a preliminary screening, not a final verdict.")


print("===== SAFEHANDS AI =====")

print("Paste your job offer below.")
print("Type END when finished.")

lines = []

while True:
    line = input()

    if line.upper() == "END":
        break

    lines.append(line)

job_description = "\n".join(lines)

check_job(job_description)