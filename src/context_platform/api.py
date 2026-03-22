"""HTTP API and HTML dashboard for the Context Engineering Platform."""

from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Form, HTTPException, Request
from pydantic import ValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.context_platform.manufacturing_worker import run_stub_manufacturing_job
from src.context_platform.context_project import get_project_id
from src.context_platform.dashboard_auth import (
    dashboard_password_configured,
    verify_dashboard_credentials,
)
from src.context_platform.middleware_dashboard_auth import SESSION_KEY
from src.context_platform.schemas import (
    ContextGapCreate,
    ContextPackageCreate,
    ContextPackageSections,
    ContextPackageUpdate,
    DeliveryPhaseCreate,
    FeatureCreate,
    ManufacturingSubmit,
    MeetingCreate,
    ProjectCreate,
    ExtractionItemReviewBody,
    MeetingExtractionConfirm,
    MeetingTranscriptUpdate,
    MeetingTypeRef,
    PhaseKind,
    RoadmapCycleCreate,
    SignOffCreate,
    SignOffRole,
    SprintCommitStoryBody,
    SprintCreate,
    StoryCreate,
    StoryQuickCreate,
    TriageQueue,
    TriageRootCauseCategory,
    TriageSubmit,
)
from src.context_platform.store import get_store

templates = Jinja2Templates(directory="templates")

api_router = APIRouter(prefix="/api/context")
page_router = APIRouter(prefix="/context", tags=["context-platform-ui"])


def _dump(m: Any) -> dict:
    return m.model_dump(mode="json")


# --- Projects ---


@api_router.get("/projects")
def api_list_projects():
    return [_dump(x) for x in get_store().list_projects()]


@api_router.post("/projects")
def api_create_project(body: ProjectCreate):
    return _dump(get_store().create_project(body))


# --- Roadmap & stories ---


@api_router.post("/roadmap-cycles")
def api_create_cycle(body: RoadmapCycleCreate):
    return _dump(get_store().create_roadmap_cycle(body))


@api_router.get("/roadmap-cycles")
def api_list_cycles():
    return [_dump(x) for x in get_store().list_roadmap_cycles()]


@api_router.post("/delivery-phases")
def api_create_phase(body: DeliveryPhaseCreate):
    try:
        return _dump(get_store().create_delivery_phase(body))
    except KeyError:
        raise HTTPException(404, "Roadmap cycle not found") from None


@api_router.get("/delivery-phases")
def api_list_phases(cycle_id: str):
    return [_dump(x) for x in get_store().list_delivery_phases(cycle_id)]


@api_router.post("/features")
def api_create_feature(body: FeatureCreate):
    try:
        return _dump(get_store().create_feature(body))
    except KeyError:
        raise HTTPException(404, "Delivery phase not found") from None


@api_router.get("/features")
def api_list_features(delivery_phase_id: str):
    return [_dump(x) for x in get_store().list_features(delivery_phase_id)]


@api_router.post("/stories")
def api_create_story(body: StoryCreate):
    try:
        return _dump(get_store().create_story(body))
    except KeyError:
        raise HTTPException(404, "Feature not found") from None


@api_router.post("/stories/quick")
def api_create_story_quick(body: StoryQuickCreate):
    """Create a story on the default backlog feature (no roadmap navigation)."""
    return _dump(
        get_store().create_story_on_default_backlog(body.title, body.description)
    )


@api_router.get("/stories")
def api_list_stories(feature_id: Optional[str] = None):
    return [_dump(x) for x in get_store().list_stories(feature_id)]


@api_router.get("/stories/{story_id}")
def api_get_story(story_id: str):
    try:
        return _dump(get_store().get_story(story_id))
    except KeyError:
        raise HTTPException(404, "Story not found") from None


@api_router.get("/roadmap-tree")
def api_roadmap_tree():
    return get_store().roadmap_tree()


# --- Sprints (D8) ---


@api_router.post("/sprints")
def api_create_sprint(body: SprintCreate):
    try:
        return _dump(get_store().create_sprint(body))
    except KeyError:
        raise HTTPException(404, "Roadmap cycle not found") from None


@api_router.get("/sprints")
def api_list_sprints():
    return [_dump(x) for x in get_store().list_sprints()]


@api_router.get("/sprints/{sprint_id}")
def api_sprint_board(sprint_id: str):
    try:
        return _dump(get_store().sprint_board(sprint_id))
    except KeyError:
        raise HTTPException(404, "Sprint not found") from None


@api_router.post("/sprints/{sprint_id}/commitments")
def api_sprint_commit(sprint_id: str, body: SprintCommitStoryBody):
    try:
        return _dump(get_store().commit_story_to_sprint(sprint_id, body))
    except KeyError:
        raise HTTPException(404, "Sprint or story not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.delete("/sprints/{sprint_id}/commitments/{story_id}")
def api_sprint_uncommit(sprint_id: str, story_id: str):
    try:
        get_store().remove_sprint_commitment(sprint_id, story_id)
    except KeyError:
        raise HTTPException(404, "Commitment not found") from None
    return {"ok": True}


# --- Context packages, gaps, manufacturing ---


@api_router.post("/stories/{story_id}/context-packages")
def api_create_package(story_id: str):
    try:
        return _dump(
            get_store().create_context_package(ContextPackageCreate(story_id=story_id))
        )
    except KeyError:
        raise HTTPException(404, "Story not found") from None


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
        raise HTTPException(404, "Story or package not found") from None


@api_router.get("/context-gaps")
def api_list_gaps(story_id: Optional[str] = None, unresolved_only: bool = False):
    return [
        _dump(x)
        for x in get_store().list_gaps(story_id=story_id, unresolved_only=unresolved_only)
    ]


@api_router.post("/context-gaps/{gap_id}/resolve")
def api_resolve_gap(gap_id: str):
    try:
        return _dump(get_store().resolve_gap(gap_id))
    except KeyError:
        raise HTTPException(404, "Gap not found") from None


@api_router.post("/context-packages/{package_id}/manufacturing")
def api_manufacturing(
    package_id: str,
    body: ManufacturingSubmit,
    background_tasks: BackgroundTasks,
):
    try:
        m = get_store().submit_manufacturing(package_id, body)
        background_tasks.add_task(run_stub_manufacturing_job, m.id)
        return _dump(m)
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
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


@api_router.get("/triage-results")
def api_list_triage_results(queue: Optional[str] = None, limit: int = 100):
    return [
        _dump(x)
        for x in get_store().list_triage_results(queue=queue, limit=limit)
    ]


@api_router.get("/meetings")
def api_list_meetings():
    return [_dump(m) for m in get_store().list_meetings()]


@api_router.get("/meetings/{meeting_id}")
def api_get_meeting(meeting_id: str):
    try:
        return _dump(get_store().get_meeting(meeting_id))
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None


@api_router.post("/meetings")
def api_create_meeting(body: MeetingCreate):
    return _dump(get_store().create_meeting(body))


@api_router.put("/meetings/{meeting_id}/transcript")
def api_meeting_transcript(meeting_id: str, body: MeetingTranscriptUpdate):
    try:
        return _dump(get_store().set_meeting_transcript(meeting_id, body))
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None


@api_router.post("/meetings/{meeting_id}/extract-stub")
def api_meeting_extract_stub(meeting_id: str):
    """Run extraction: OpenAI when `OPENAI_API_KEY` is set, else DECISION:/ACTION:/REQ: stub."""
    try:
        return _dump(get_store().run_meeting_extraction_stub(meeting_id))
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.get("/decision-records")
def api_list_decisions(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    decision_code: Optional[str] = None,
    limit: int = 100,
):
    return [
        _dump(x)
        for x in get_store().list_decision_records(
            entity_type=entity_type,
            entity_id=entity_id,
            decision_code=decision_code,
            limit=limit,
        )
    ]


@api_router.get("/artifacts")
def api_list_artifacts(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    artifact_kind: Optional[str] = None,
    limit: int = 100,
):
    return [
        _dump(x)
        for x in get_store().list_artifacts(
            entity_type=entity_type,
            entity_id=entity_id,
            artifact_kind=artifact_kind,
            limit=limit,
        )
    ]


@api_router.get("/audit-events")
def api_list_audit(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
):
    return [
        _dump(x)
        for x in get_store().list_audit_events(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            limit=limit,
        )
    ]


@api_router.get("/improvement-items")
def api_list_improvements(status: Optional[str] = "open", limit: int = 200):
    return [_dump(x) for x in get_store().list_improvement_items(status=status, limit=limit)]


@api_router.post("/improvement-items/{item_id}/resolve")
def api_resolve_improvement(item_id: str):
    try:
        return _dump(get_store().resolve_improvement_item(item_id))
    except KeyError:
        raise HTTPException(404, "Improvement item not found") from None


@api_router.post("/meetings/{meeting_id}/extraction-items/{item_index}/review")
def api_extraction_item_review(
    meeting_id: str,
    item_index: int,
    body: ExtractionItemReviewBody,
):
    try:
        return _dump(
            get_store().set_meeting_extraction_item_review(
                meeting_id, item_index, body.decision
            )
        )
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.post("/meetings/{meeting_id}/extraction-accept-all")
def api_extraction_accept_all(meeting_id: str):
    try:
        return _dump(get_store().meeting_extraction_accept_all(meeting_id))
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@api_router.post("/meetings/{meeting_id}/confirm-extraction")
def api_meeting_confirm(
    meeting_id: str,
    body: MeetingExtractionConfirm = Body(default_factory=MeetingExtractionConfirm),
):
    try:
        return _dump(get_store().confirm_meeting_extraction(meeting_id, body))
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


# --- HTML dashboard ---


def _dashboard_context(request: Request) -> dict[str, Any]:
    store = get_store()
    tree = store.roadmap_tree()
    sprint_boards = [store.sprint_board(sp.id) for sp in store.list_sprints()]
    story_blocks = []
    for s in store.list_stories():
        pkgs = store.list_packages_for_story(s.id)
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
        story_blocks.append({"story": s, "packages": pkg_views})
    return {
        "request": request,
        "projects": store.list_projects(),
        "current_project_id": get_project_id(),
        "roadmap_tree": tree,
        "story_blocks": story_blocks,
        "gaps": store.list_gaps(unresolved_only=True),
        "meetings": store.list_meetings(),
        "audit_events": store.list_audit_events(limit=30),
        "decision_records": store.list_decision_records(limit=25),
        "artifacts": store.list_artifacts(limit=25),
        "open_improvements": store.list_improvement_items(status="open", limit=40),
        "sprint_boards": sprint_boards,
        "allow_unapproved_sprint_env": store.allow_unapproved_sprint_commit_env(),
        "root_cause_categories": [e.value for e in TriageRootCauseCategory],
        "phase_kinds": [e.value for e in PhaseKind],
        "roles": [e.value for e in SignOffRole],
        "queues": [e.value for e in TriageQueue],
        "meeting_types": [e.value for e in MeetingTypeRef],
        "dashboard_login_enabled": dashboard_password_configured(),
        "package_json_example": json.dumps(
            {
                "business_context": {
                    "summary": "User can reset password",
                    "business_rules": ["Token expires in 1h"],
                    "user_stories": [
                        {
                            "title": "Reset password",
                            "given_when_then": "Given logged out...",
                        }
                    ],
                },
                "technical_approach": {
                    "components": [{"name": "AuthService", "responsibility": "tokens"}],
                    "files_to_touch": ["src/auth.py"],
                    "patterns": ["repository"],
                    "error_handling": "Map 401 to login",
                },
                "testing_contract": {
                    "preconditions": ["User exists"],
                    "postconditions": ["Password changed"],
                    "invariants": ["Session invalidated"],
                    "scenarios": [
                        {"name": "happy path", "scenario_type": "happy_path", "steps": "..."}
                    ],
                },
            },
            indent=2,
        ),
    }


@page_router.get("/login", response_class=HTMLResponse)
def dashboard_login_get(request: Request, next: str = "/context"):
    if not dashboard_password_configured():
        return RedirectResponse(url="/context", status_code=302)
    return templates.TemplateResponse(
        "dashboard_login.html",
        {"request": request, "next": next, "error": None},
    )


@page_router.post("/login")
def dashboard_login_post(
    request: Request,
    username: str = Form(""),
    password: str = Form(...),
    next: str = Form("/context"),
):
    if not dashboard_password_configured():
        return RedirectResponse(url="/context", status_code=302)
    if not verify_dashboard_credentials(username, password):
        return templates.TemplateResponse(
            "dashboard_login.html",
            {
                "request": request,
                "next": next,
                "error": "Invalid username or password.",
            },
            status_code=200,
        )
    request.session[SESSION_KEY] = True
    dest = next if next.startswith("/") else "/context"
    return RedirectResponse(url=dest, status_code=303)


@page_router.post("/logout")
def dashboard_logout(request: Request):
    if dashboard_password_configured():
        request.session.clear()
    return RedirectResponse(url="/context/login", status_code=303)


@page_router.get("", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("context_dashboard.html", _dashboard_context(request))


@page_router.post("/set-project")
def form_set_project(request: Request, project_id: str = Form(...)):
    try:
        get_store().get_project(project_id)
    except KeyError:
        raise HTTPException(404, "Project not found") from None
    resp = RedirectResponse(url="/context", status_code=303)
    resp.set_cookie(
        "context_project_id",
        project_id,
        max_age=365 * 24 * 3600,
        httponly=True,
        samesite="lax",
    )
    return resp


@page_router.post("/projects")
def form_create_project(request: Request, name: str = Form(...)):
    get_store().create_project(ProjectCreate(name=name))
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/roadmap-cycles")
def form_create_cycle(request: Request, name: str = Form(...)):
    get_store().create_roadmap_cycle(RoadmapCycleCreate(name=name))
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/delivery-phases")
def form_create_phase(
    request: Request,
    roadmap_cycle_id: str = Form(...),
    name: str = Form(...),
    phase_kind: str = Form("discovery"),
    sort_order: int = Form(0),
):
    try:
        get_store().create_delivery_phase(
            DeliveryPhaseCreate(
                roadmap_cycle_id=roadmap_cycle_id,
                name=name,
                phase_kind=PhaseKind(phase_kind),
                sort_order=sort_order,
            )
        )
    except ValueError:
        raise HTTPException(400, "Invalid phase kind") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/features")
def form_create_feature(
    request: Request,
    delivery_phase_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
):
    get_store().create_feature(
        FeatureCreate(
            delivery_phase_id=delivery_phase_id, title=title, description=description
        )
    )
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/stories")
def form_create_story(
    request: Request,
    feature_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
):
    try:
        get_store().create_story(
            StoryCreate(feature_id=feature_id, title=title, description=description)
        )
    except KeyError:
        raise HTTPException(404, "Feature not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/stories/quick")
def form_story_quick(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
):
    get_store().create_story_on_default_backlog(title, description)
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/sprints")
def form_create_sprint(
    request: Request,
    name: str = Form(...),
    roadmap_cycle_id: str = Form(""),
    capacity_notes: str = Form(""),
):
    try:
        get_store().create_sprint(
            SprintCreate(
                name=name,
                roadmap_cycle_id=roadmap_cycle_id.strip() or None,
                capacity_notes=capacity_notes,
            )
        )
    except KeyError:
        raise HTTPException(404, "Roadmap cycle not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/sprints/{sprint_id}/commitments")
def form_sprint_commit(
    request: Request,
    sprint_id: str,
    story_id: str = Form(...),
    sort_order: int = Form(0),
    allow_unapproved: Optional[str] = Form(None),
):
    try:
        get_store().commit_story_to_sprint(
            sprint_id,
            SprintCommitStoryBody(
                story_id=story_id,
                sort_order=sort_order,
                allow_unapproved=allow_unapproved in ("1", "on", "true", "yes"),
            ),
        )
    except KeyError:
        raise HTTPException(404, "Sprint or story not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/sprints/{sprint_id}/commitments/{story_id}/remove")
def form_sprint_uncommit(request: Request, sprint_id: str, story_id: str):
    try:
        get_store().remove_sprint_commitment(sprint_id, story_id)
    except KeyError:
        raise HTTPException(404, "Commitment not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/stories/{story_id}/packages")
def form_create_package(request: Request, story_id: str):
    try:
        get_store().create_context_package(ContextPackageCreate(story_id=story_id))
    except KeyError:
        raise HTTPException(404, "Story not found") from None
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
    background_tasks: BackgroundTasks,
    submitted_by: str = Form(...),
):
    try:
        m = get_store().submit_manufacturing(
            package_id, ManufacturingSubmit(submitted_by=submitted_by)
        )
        background_tasks.add_task(run_stub_manufacturing_job, m.id)
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
    feedback: str = Form(""),
    gap_lines: str = Form(""),
    root_cause_category: str = Form(""),
    root_cause_narrative: str = Form(""),
):
    gaps = [ln.strip() for ln in gap_lines.replace("\r", "").split("\n") if ln.strip()]
    cat: Optional[TriageRootCauseCategory] = None
    if root_cause_category.strip():
        try:
            cat = TriageRootCauseCategory(root_cause_category.strip())
        except ValueError:
            raise HTTPException(400, "Invalid root_cause_category") from None
    try:
        body = TriageSubmit(
            queue=TriageQueue(queue),
            feedback=feedback,
            gap_items=gaps,
            root_cause_category=cat,
            root_cause_narrative=root_cause_narrative or None,
        )
        get_store().submit_triage(request_id, body)
    except KeyError:
        raise HTTPException(404, "Manufacturing request not found") from None
    except ValidationError as e:
        raise HTTPException(422, detail=e.errors()) from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/gaps")
def form_create_gap(
    request: Request,
    story_id: str = Form(...),
    description: str = Form(...),
    meeting_hint: str = Form(""),
    severity: str = Form("medium"),
):
    try:
        get_store().create_gap(
            ContextGapCreate(
                story_id=story_id,
                description=description,
                meeting_hint=meeting_hint,
                severity=severity,
            )
        )
    except KeyError:
        raise HTTPException(404, "Story not found") from None
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


@page_router.post("/meetings/{meeting_id}/transcript")
def form_meeting_transcript(
    request: Request,
    meeting_id: str,
    transcript: str = Form(...),
):
    try:
        get_store().set_meeting_transcript(
            meeting_id, MeetingTranscriptUpdate(text=transcript)
        )
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/meetings/{meeting_id}/extract-stub")
def form_meeting_extract(request: Request, meeting_id: str):
    try:
        get_store().run_meeting_extraction_stub(meeting_id)
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/meetings/{meeting_id}/confirm-extraction")
def form_meeting_confirm(request: Request, meeting_id: str):
    try:
        get_store().confirm_meeting_extraction(meeting_id, MeetingExtractionConfirm())
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/meetings/{meeting_id}/extraction-items/{item_index}/review")
def form_extraction_item_review(
    request: Request,
    meeting_id: str,
    item_index: int,
    decision: str = Form(...),
):
    if decision not in ("accept", "reject"):
        raise HTTPException(400, "decision must be accept or reject")
    try:
        get_store().set_meeting_extraction_item_review(meeting_id, item_index, decision)
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/meetings/{meeting_id}/extraction-accept-all")
def form_extraction_accept_all(request: Request, meeting_id: str):
    try:
        get_store().meeting_extraction_accept_all(meeting_id)
    except KeyError:
        raise HTTPException(404, "Meeting not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return RedirectResponse(url="/context", status_code=303)


@page_router.post("/improvement-items/{item_id}/resolve")
def form_resolve_improvement(request: Request, item_id: str):
    try:
        get_store().resolve_improvement_item(item_id)
    except KeyError:
        raise HTTPException(404, "Improvement item not found") from None
    return RedirectResponse(url="/context", status_code=303)
