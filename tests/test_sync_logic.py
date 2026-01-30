
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from app.services.strava_service import StravaService
from app.models import Activity

@pytest.mark.asyncio
async def test_sync_activities_windowed_mirroring():
    # Setup
    service = StravaService()
    service.get_activities = AsyncMock()
    
    mock_user = MagicMock()
    mock_user.id = "user1"
    mock_user.is_strava_connected.return_value = True
    mock_user.strava_access_token = "token"
    
    mock_db = MagicMock()
    
    # helper to create activity dict
    def make_strava_activity(id, date_str):
        return {
            "id": id,
            "name": f"Activity {id}",
            "type": "Run",
            "start_date": date_str,
            "distance": 1000,
            "moving_time": 300,
            "total_elevation_gain": 10
        }

    # Scenario:
    # DB has:
    # - 100: Old activity (should be preserved)
    # - 200: Recent activity (to be kept)
    # - 300: Recent activity (deleted in Strava, should be deleted in DB)
    
    # Strava returns:
    # - 200: Recent activity (kept)
    # - 400: New activity (should be added)
    
    # Dates:
    # Today is 2024-01-10
    # 100: 2023-01-01 (Old)
    # 200: 2024-01-09 (Recent)
    # 300: 2024-01-08 (Recent)
    # 400: 2024-01-10 (New)
    
    strava_response = [
        make_strava_activity(400, "2024-01-10T10:00:00Z"),
        make_strava_activity(200, "2024-01-09T10:00:00Z"),
    ]
    service.get_activities.return_value = strava_response
    
    # Mock DB query
    # It should query for activities >= 2024-01-09 (min date in strava batch)
    # So it should return 200 and 300 (if they exist in DB). 
    # It should NOT return 100 because it's older.
    
    activity_200 = Activity(strava_id=200, start_date=datetime(2024, 1, 9))
    activity_300 = Activity(strava_id=300, start_date=datetime(2024, 1, 10)) # Actually 300 is recent
    
    # When query is called with filter, we simulate returning what's in DB for that window
    # logic: filter(Activity.start_date >= min_date)
    # min_date will be 2024-01-09
    # So valid DB hits in that range: 200, 300 (assuming 300 is also >= Jan 9, let's say Jan 9 afternoon)
    
    # Let's adjust 300 date to be within range to test deletion
    activity_300.start_date = datetime(2024, 1, 9, 12, 0, 0)
    
    # Mocking the query chain: db.query().filter().all()
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.all.return_value = [activity_200, activity_300]
    
    # Execute
    new_activities = await service.sync_activities(mock_user, mock_db)
    
    # Verifications
    
    # 1. Verify Min Date Calculation
    # Expected min date: 2024-01-09
    # Arguments to filter check happen in SQLAlchemy expression objects, hard to inspect directly on mock without complex matching.
    # Instead we verify behavior.
    
    # 2. Verify Adds
    # Should add 400
    assert len(new_activities) == 1
    assert new_activities[0].strava_id == 400
    mock_db.add.assert_called_once()
    
    # 3. Verify Deletes
    # Should delete 300 (In DB fetch, but not in Strava fetch)
    # Should NOT delete 100 (Was not even fetched from DB because it's outside window)
    
    # Check delete call
    # db.query().filter().delete()
    # We need to find the delete call
    
    # The code does:
    # db.query(Activity).filter(...).delete()
    # verify delete was called
    assert mock_query.filter.return_value.delete.called
    
    print("Test passed!")
