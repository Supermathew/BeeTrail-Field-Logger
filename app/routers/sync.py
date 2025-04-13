from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_db, get_current_user
from app.db.crud import get_user_sync_token, update_user_sync_token, get_changes_since_sync
from datetime import datetime,timezone
from app.models.sync import SyncTokenResponse, SyncDataResponse, SyncRequest

router = APIRouter(tags=["sync"])

@router.get("/api/sync", response_model=SyncTokenResponse)
async def get_sync_token(db=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    sync_token = await get_user_sync_token(current_user["email"])
    print(sync_token)
    if not sync_token:
        sync_token = datetime.utcnow().timestamp()
        await update_user_sync_token(current_user["email"])

    return {"syncToken": sync_token}

@router.post("/api/sync/hives", response_model=SyncDataResponse)
async def sync_hives(sync_data: SyncRequest, db=Depends(get_db), current_user=Depends(get_current_user)):
    if sync_data.changes:
        for change in sync_data.changes:
            if "localTimestamp" in change:
                try:
                    change["lastModified"] = datetime.fromisoformat(change["localTimestamp"])
                except ValueError:
                    change["lastModified"] = datetime.now(timezone.utc)
            else:
                change["lastModified"] = datetime.now(timezone.utc)

            existing_hive = await db["hives"].find_one({"hiveId": change["hiveId"]})
            if existing_hive:
                print("existing ha")
                change_id = change.pop("_id", None)
                await db["hives"].update_one(
                    {"hiveId": change["hiveId"]},
                    {"$set": change}
                )
            else:
                change_id = change.pop("_id", None)
                print("mathew")
                await db["hives"].insert_one(change)

    server_changes = await get_changes_since_sync("hives", sync_data.syncToken)
    new_sync_token = await update_user_sync_token(current_user["email"])

    return {
        "syncToken": new_sync_token,
        "changes": server_changes
    }
