from datetime import datetime

from models import APPROVAL_STEPS, Approval, Request, db


def generate_request_no():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"WP-{today}-"
    last = (
        Request.query.filter(Request.request_no.like(f"{prefix}%"))
        .order_by(Request.id.desc())
        .first()
    )
    if last:
        try:
            seq = int(last.request_no.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"


def process_approval(request, user, decision, comment=""):
    approval = Approval(
        request_id=request.id,
        approver_role=user.role,
        approver_name=user.full_name,
        decision=decision,
        comment=comment,
    )
    db.session.add(approval)

    if decision == "rejected":
        request.status = "rejected"
        request.current_step = ""
        db.session.commit()
        return

    try:
        idx = APPROVAL_STEPS.index(request.current_step)
    except ValueError:
        idx = -1

    if idx < len(APPROVAL_STEPS) - 1:
        request.current_step = APPROVAL_STEPS[idx + 1]
    else:
        request.status = "approved"
        request.current_step = ""

    db.session.commit()
