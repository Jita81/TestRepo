"""HTTP API and HTML dashboard for the Context Engineering Platform MVP."""

from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.context_platform.schemas import (
    ContextGapCreate,
    ContextPackageCreate,
    ContextPackageSections,
    ContextPackageUpdate,
    ManufacturingSubmit,
    MeetingCreate,
    MeetingTypeRef,
    Phase,
    SignOffCreate,
    SignOffRole,
    TriageQueue,
    TriageSubmit,
    WorkItemCreate,
)
from src.context_platform.store import get_store

templates = Jinja2Templates(directory="templates")

api_router = APIRouter(prefix="/api/context")
page_router = APIRouter(prefix="/context", tags=["context-platform-ui"])


def _dump(m: Any) -> dict:
    return m.model_dump(mode="json")


# --- JSON API ---


@api_router.post("/work-items")
def api_create_work_item(body: WorkItemCreate):
    try:
        return _dump(get_store().create_work_item(body))
    except Exception as e:
        raise HTTPException(400, str(e)) from e


@api_router.get("/work-items")
def api_list_work_items():
    return [_dump(x) for x in get_store().list_work_items()]


@api_router.get("/work-items/{work_item_id}")
def api_get_work_item(work_item_id: str):
    try:
        return _dump(get_store().get_work_item(work_item_id))
    except KeyError:
        raise HTTPException(404, "Work item not found") from None


@api_router.post("/work-items/{work_item_id}/context-packages")
def api_create_package(work_item_id: str):
    try:
        return _dump(
            get_store().create_context_package(
                ContextPackageCreate(work_item_id=work_item_id)
            )
        )
    except KeyError:
        raise HTTPException(404, "Work item not found") from None


@api_router.get("/context-packages/{package_id}")
def api_get_package(package_id: str):
    try:
        return _dump(get_store().get_context_package(package_id))
    except KeyError:
        raise HTTPException(404, "Context package not found") from None


@api_router.patch("/context-packages/{package_id}")
def api_update_package(package_id: str, body: ContextPackageUpdate):
    try:
        return _dump(get_store().update_context_package(package_id, body))
    except KeyError:
        raise HTTPException(404, "Context package not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.post("/context-packages/{package_id}/sign-offs")
def api_sign_off(package_id: str, body: SignOffCreate):
    try:
        return _dump(get_store().add_sign_off(package_id, body))
    except KeyError:
        raise HTTPException(404, "Context package not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.post("/context-gaps")
def api_create_gap(body: ContextGapCreate):
    try:
        return _dump(get_store().create_gap(body))
    except KeyError:
        raise HTTPException(404, "Work item or package not found") from None


@api_router.get("/context-gaps")
def api_list_gaps(work_item_id: Optional[str] = None, unresolved_only: bool = False):
    return [
        _dump(x)
        for x in get_store().list_gaps(
            work_item_id=work_item_id, unresolved_only=unresolved_only
        )
    ]


@api_router.post("/context-gaps/{gap_id}/resolve")
def api_resolve_gap(gap_id: str):
    try:
        return _dump(get_store().resolve_gap(gap_id))
    except KeyError:
        raise HTTPException(404, "Gap not found") from None


@api_router.post("/context-packages/{package_id}/manufacturing")
def api_manufacturing(package_id: str, body: ManufacturingSubmit):
    try:
        return _dump(get_store().submit_manufacturing(package_id, body))
    except KeyError:
        raise HTTPException(404, "Context package not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.post("/manufacturing/{request_id}/triage")
def api_triage(request_id: str, body: TriageSubmit):
    try:
        return _dump(get_store().submit_triage(request_id, body))
    except KeyError:
        raise HTTPException(404, "Manufacturing request not found") from None


@api_router.get("/meetings")
def api_list_meetings():
    return [_dump(m) for m in get_store().list_meetings()]


@api_router.post("/meetings")
def api_create_meeting(body: MeetingCreate):
    return _dump(get_store().create_meeting(body))


# --- HTML dashboard (form posts) ---


def _dashboard_context(request: Request) -> dict[str, Any]:
    store = get_store()
    items = store.list_work_items()
    work_blocks = []
    for wi in items:
        pkgs = store.list_packages_for_work_item(wi.id)
        pkg_views = []
        for p in pkgs:
            mfg = store.list_manufacturing_for_package(p.id)
            mfg_views = []
            for m in mfg:
                tri = store.get_latest_triage_for_request(m.id)
                mfg_views.append({"m": m, "triage": tri})
            pkg_views.append(
                {
                    "pkg": p,
                    "manufacturing": mfg_views,
                    "business_json": json.dumps(p.business_context, indent=2),
                    "technical_json": json.dumps(p.technical_approach, indent=2),
                    "testing_json": json.dumps(p.testing_contract, indent=2),
                }
            )
        work_blocks.append({"item": wi, "packages": pkg_views})
    return {
        "request": request,
        "work_blocks": work_blocks,
        "gaps": store.list_gaps(unresolved_only=True),
        "meetings": store.list_meetings(),
        "phases": [e.value for e in Phase],
        "roles": [e.value for e in SignOffRole],
        "queues": [e.value for e in TriageQueue],
        "meeting_types": [e.value for e in MeetingTypeRef],
    }


@page_router.get("", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("context_dashboard.html", _dashboard_context(request))


@page_router.post("/work-items")
def form_create_work_item(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    phase: str = Form("discovery"),
):
    try:
        get_store().create_work_item(
            WorkItemCreate(title=title, description=description, phase=Phase(phase))
        )
    except ValueError:
        raise HTTPException(400, "Invalid phase") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/work-items/{work_item_id}/packages")
def form_create_package(request: Request, work_item_id: str):
    try:
        get_store().create_context_package(ContextPackageCreate(work_item_id=work_item_id))
    except KeyError:
        raise HTTPException(404, "Work item not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/packages/{package_id}/sections")
def form_update_sections(
    request: Request,
    package_id: str,
    business_json: str = Form("{}"),
    technical_json: str = Form("{}"),
    testing_json: str = Form("{}"),
):
    try:
        business = json.loads(business_json or "{}")
        technical = json.loads(technical_json or "{}")
        testing = json.loads(testing_json or "{}")
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON in sections") from None
    try:
        get_store().update_context_package(
            package_id,
            ContextPackageUpdate(
                sections=ContextPackageSections(
                    business_context=business,
                    technical_approach=technical,
                    testing_contract=testing,
                )
            ),
        )
    except KeyError:
        raise HTTPException(404, "Package not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/packages/{package_id}/sign-off")
def form_sign_off(
    request: Request,
    package_id: str,
    role: str = Form(...),
    signed_by: str = Form(...),
):
    try:
        get_store().add_sign_off(
            package_id, SignOffCreate(role=SignOffRole(role), signed_by=signed_by)
        )
    except KeyError:
        raise HTTPException(404, "Package not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/packages/{package_id}/manufacturing")
def form_manufacturing(
    request: Request,
    package_id: str,
    submitted_by: str = Form(...),
):
    try:
        get_store().submit_manufacturing(
            package_id, ManufacturingSubmit(submitted_by=submitted_by)
        )
    except KeyError:
        raise HTTPException(404, "Package not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/manufacturing/{request_id}/triage")
def form_triage(
    request: Request,
    request_id: str,
    queue: str = Form(...),
    feedback: str = Form(...),
):
    try:
        get_store().submit_triage(
            request_id, TriageSubmit(queue=TriageQueue(queue), feedback=feedback)
        )
    except KeyError:
        raise HTTPException(404, "Manufacturing request not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/gaps")
def form_create_gap(
    request: Request,
    work_item_id: str = Form(...),
    description: str = Form(...),
    meeting_hint: str = Form(""),
    severity: str = Form("medium"),
):
    try:
        get_store().create_gap(
            ContextGapCreate(
                work_item_id=work_item_id,
                description=description,
                meeting_hint=meeting_hint,
                severity=severity,
            )
        )
    except KeyError:
        raise HTTPException(404, "Work item not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/gaps/{gap_id}/resolve")
def form_resolve_gap(request: Request, gap_id: str):
    try:
        get_store().resolve_gap(gap_id)
    except KeyError:
        raise HTTPException(404, "Gap not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/meetings")
def form_create_meeting(
    request: Request,
    meeting_type: str = Form(...),
    title: str = Form(""),
):
    try:
        get_store().create_meeting(
            MeetingCreate(meeting_type=MeetingTypeRef(meeting_type), title=title)
        )
    except ValueError:
        raise HTTPException(400, "Invalid meeting type") from None
    return RedirectResponse(url="/context", status_code=303)
