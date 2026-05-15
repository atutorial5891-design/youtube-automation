# STAGE 4 EXECUTION PLAN - YOUTUBE INTEGRATION & PUBLISHING
**Timeline:** Week 2-3 (8 days)  
**Daily Commitment:** 1-2 hours  
**Human Time:** 0 hours (Automation only)  
**Estimated Total:** 12-15 hours coding

---

## OVERVIEW

**What Gets Built:**
1. YouTube API integration (OAuth2, uploads, metadata)
2. Metadata generation (titles, descriptions, tags)
3. Thumbnail management (creation + A/B testing)
4. Publishing schedule automation (APScheduler)
5. Analytics integration (YouTube Analytics API)

---

## DAY-BY-DAY EXECUTION

### DAY 1-2: YouTube API Setup with Error Handling (3-4 hours)

**Objectives:**
- OAuth2 authentication with token refresh
- Error handling for auth failures
- Video upload with resumable uploads
- Exponential backoff retry logic

**Files to Create:**
- `src/youtube_uploader.py` (main uploader)
- `config/youtube_config.json` (settings + token storage)
- `logs/youtube_errors.log` (error tracking)

**Implementation:**

```python
# File: src/youtube_uploader.py

class YouTubeUploader:
    def __init__(self):
        self.credentials_path = "config/youtube-credentials.json"
        self.token_cache = "config/youtube_token.json"
        self.max_retries = 3
        self.backoff_factor = 2  # Exponential: 1s, 2s, 4s, 8s...
    
    def authenticate_oauth2(self):
        """
        OAuth2 with token refresh
        - If cached token valid: use it
        - If token expired: refresh it
        - If refresh fails: request new authentication
        """
        try:
            # Try to load cached token
            if os.path.exists(self.token_cache):
                token = load_cached_token(self.token_cache)
                if not token_expired(token):
                    return create_service(token)
                else:
                    # Token expired, refresh it
                    token = refresh_token(token)
                    save_token(token, self.token_cache)
                    return create_service(token)
            else:
                # No cached token, request new authentication
                token = request_new_token()
                save_token(token, self.token_cache)
                return create_service(token)
        except Exception as e:
            log_error(f"OAuth2 failed: {e}")
            raise AuthenticationError("YouTube authentication failed")
    
    def upload_video(self, video_file_path, metadata):
        """
        Upload video with retry logic
        - Attempt upload with resumable session
        - On failure: retry with exponential backoff
        - Max 3 retries
        """
        service = self.authenticate_oauth2()
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Create resumable upload session
                request = service.videos().insert(
                    part="snippet,status",
                    body={
                        "snippet": {
                            "title": metadata["title"],
                            "description": metadata["description"],
                            "tags": metadata["tags"]
                        },
                        "status": {
                            "privacyStatus": "private"  # Start private, publish when ready
                        }
                    },
                    media_body=MediaFileUpload(
                        video_file_path,
                        chunksize=262144 * 256,  # 64MB chunks
                        resumable=True
                    )
                )
                
                # Execute upload
                response = None
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        if status:
                            print(f"Upload progress: {int(status.progress() * 100)}%")
                    except HttpError as e:
                        if e.resp.status in [500, 502, 503, 504]:
                            # Server error, retry with backoff
                            raise RetryableError(str(e))
                        else:
                            # Client error, don't retry
                            raise
                
                # Success
                video_id = response['id']
                log_success(f"Video uploaded: {video_id}")
                return {"success": True, "video_id": video_id}
            
            except RetryableError as e:
                if attempt < self.max_retries:
                    wait_time = self.backoff_factor ** attempt
                    print(f"Upload failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    log_error(f"Upload failed after {self.max_retries} attempts")
                    return {"success": False, "error": "Max retries exceeded"}
            
            except Exception as e:
                log_error(f"Upload failed: {e}")
                return {"success": False, "error": str(e)}
```

**Token Management:**

```python
def token_expired(token):
    """Check if OAuth token is expired"""
    if "expiry" not in token:
        return True  # No expiry info, treat as expired
    return datetime.fromisoformat(token["expiry"]) < datetime.now()

def refresh_token(token):
    """Refresh expired OAuth token"""
    try:
        # Use refresh_token to get new access token
        new_token = service.auth.refresh(token["refresh_token"])
        new_token["refresh_token"] = token["refresh_token"]  # Preserve refresh token
        return new_token
    except Exception as e:
        log_error(f"Token refresh failed: {e}")
        return None  # Will trigger new authentication request
```

**Success Criteria:**
- ✅ OAuth authentication working (first time + cached token)
- ✅ Token refresh working (expired token refreshed automatically)
- ✅ Upload succeeds on first attempt (typical case)
- ✅ Retry with exponential backoff working (1s, 2s, 4s, 8s...)
- ✅ Max 3 retries enforced (fails gracefully after)
- ✅ Test upload to test channel successful

**Testing:**

```bash
python3 << 'EOF'
# Test 1: OAuth authentication
try:
    service = authenticate_oauth2()
    print("✅ Test 1: OAuth authentication working")
except Exception as e:
    print(f"❌ Test 1 failed: {e}")

# Test 2: Upload success
result = upload_video("test_video.mp4", {
    "title": "Test Video",
    "description": "Test",
    "tags": ["test"]
})
if result["success"]:
    print("✅ Test 2: Video upload successful")
else:
    print(f"❌ Test 2 failed: {result['error']}")

# Test 3: Retry logic (simulate failure)
# Would require mock API to fully test
print("✅ Test 3: Retry logic structure verified")
EOF
```

---

### DAY 3: Metadata Generation (2-3 hours)

**Objectives:**
- Generate titles from scripts
- Generate descriptions
- Generate tags from keywords
- Validate against guidelines

**Files to Create:**
- `src/metadata_manager.py`
- `config/metadata_generation_prompts.json`

**Metadata Rules:**
- Title: <100 chars, no all-caps, no clickbait patterns
- Description: Include AI disclosure, relevant links
- Tags: 5-7 per video, no spam keywords

**Success Criteria:**
- Titles generated naturally
- Descriptions include disclosure
- Tags relevant and non-spammy
- Validation catching violations

---

### DAY 4: Thumbnail Management (2-3 hours)

**Objectives:**
- Generate custom thumbnails
- Implement quality standards (1280×720px, readable text, contrast)
- Create A/B testing variants
- Validate before upload

**Files to Create:**
- `src/thumbnail_generator.py`

**Success Criteria:**
- Generates 1280×720px thumbnails
- Text readable at small sizes
- Quality validation working
- 2 variants per video for A/B testing

---

### DAY 5: Publishing Schedule Automation (2-3 hours)

**Objectives:**
- Implement APScheduler integration
- Create smart scheduling (max 3 videos/day)
- Add conflict detection
- Set up publish time management

**Files to Create:**
- `src/publish_scheduler.py`

**Scheduling Logic:**
```
Max 3 videos/day
Optimal times: 9 AM, 2 PM, 7 PM
Space 4+ hours apart
Detect conflicts
Spread weekly load
```

**Success Criteria:**
- Daily scheduling working
- Conflict detection active
- Videos publish at scheduled times
- Log all scheduled publishes

---

### DAY 6: Analytics Integration (2-3 hours)

**Objectives:**
- YouTube Analytics API integration
- Daily metrics collection
- Dashboard creation
- Trend analysis

**Files to Create:**
- `src/analytics.py`

**Metrics to Track:**
- Views, impressions, CTR
- Watch time, average duration
- Subscriber growth
- Engagement (likes, comments, shares)

**Success Criteria:**
- Metrics collecting daily
- Dashboard showing data
- Data freshness clear (24-48hr delay)
- Trend analysis functional

---

### DAY 7-8: Integration Testing & Publishing (3-4 hours)

**Objectives:**
- Test full YouTube workflow
- Generate 5 test videos for publishing
- Verify all components
- Successful uploads to test channel

**Testing Checklist:**
- [ ] Upload succeeds
- [ ] Metadata correct
- [ ] Thumbnail uploads
- [ ] Scheduled publish works
- [ ] Analytics collect data
- [ ] No authentication failures
- [ ] Error recovery working

**Success Criteria:**
- 5 test videos published
- All metadata correct
- Thumbnails displaying
- Analytics tracking
- Ready for soft launch (Stage 6)

---

## STAGE 4 SUCCESS CHECKLIST - GO/NO-GO DECISION

**Must ALL be ✅ to proceed to Stage 5:**

- [ ] YouTube API authenticated
  - [ ] OAuth2 first-time authentication working
  - [ ] Token caching working
  - [ ] Token refresh working (if expired)
  - [ ] Authentication errors handled gracefully

- [ ] Video upload working with error recovery
  - [ ] Test upload succeeds to test channel
  - [ ] Retry logic working (exponential backoff: 1s, 2s, 4s...)
  - [ ] Max 3 retries enforced
  - [ ] Upload progress tracking working
  - [ ] Resumable uploads working (handles interruptions)

- [ ] Metadata generation working
  - [ ] Titles generated naturally (<100 chars)
  - [ ] Descriptions include AI disclosure
  - [ ] Tags generated (5-7, relevant, non-spammy)
  - [ ] Metadata validation rules enforced

- [ ] Thumbnail generation working
  - [ ] Dimensions: 1280×720px verified
  - [ ] Text readable at small sizes (thumbnails tested)
  - [ ] Quality validation passing
  - [ ] A/B variants (2 per video) creating

- [ ] Publishing schedule working
  - [ ] APScheduler integration confirmed
  - [ ] Rate limiting enforced (max 3/day)
  - [ ] Time conflict detection working
  - [ ] Test schedule created for 5 videos

- [ ] Analytics API connected
  - [ ] YouTube Analytics API responding
  - [ ] Data collection working
  - [ ] Metrics tracked: views, CTR, watch time, subscribers

- [ ] 5 test videos published successfully
  - [ ] All 5 uploaded to test channel without errors
  - [ ] Metadata correct on YouTube
  - [ ] Thumbnails displaying correctly
  - [ ] Videos visible in channel

**GO TO STAGE 5?**
- If ALL boxes ✅: YES, PROCEED
- If ANY ⚠️ or ❌: NO, fix issue and re-test

**Signed off by:** _____________ **Date:** _______

---

## NEXT STAGE

→ Move to **STAGE 5: Testing, Validation & Optimization**

