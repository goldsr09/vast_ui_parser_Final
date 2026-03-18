# Broken Wrapper Detection for VAST Parser

This enhancement adds functionality to detect and track wrapped ads that lead to empty VAST responses, helping you identify broken ad serving endpoints.

## Features

### 🔍 **Broken Wrapper Detection**
- Automatically detects when a wrapper URL returns an empty VAST response
- Identifies VAST responses with `NO_AD` status (like the example in the image)
- Tracks wrapper chains to show the full path to the broken URL
- Stores detailed information about broken wrappers in the database

### 📊 **Broken Wrapper Dashboard**
- Dedicated page to view all broken wrapper URLs
- Summary statistics showing frequency of broken URLs
- Detailed view of wrapper chains leading to broken endpoints
- Timeline tracking (first seen, last seen)

### 🔔 **Alert System**
- Immediate alerts when broken wrappers are detected during parsing
- Visual indicators in the results table
- API endpoint for integration with monitoring systems

### 🛠 **API Integration**
- REST API endpoint for broken wrapper statistics
- JSON response format for easy integration
- Real-time statistics and metrics

## How It Works

### Detection Logic
1. **Empty VAST Detection**: Checks for VAST responses with no `<Ad>` elements
2. **NO_AD Status**: Specifically looks for `status="NO_AD"` attributes in VAST responses
3. **Wrapper Chain Tracking**: Follows the complete chain of wrapper URLs
4. **Broken URL Identification**: Identifies the specific URL that returns empty content

### Database Schema
Two new columns are added to the `vast_ads` table:
- `broken_wrapper_url`: The URL that returns empty VAST response
- `wrapper_chain`: JSON array of the complete wrapper chain

## Usage

### Web Interface

1. **Parse VAST URLs**: Use the existing parsing functionality
   ```
   http://localhost:5000/
   ```

2. **View Broken Wrappers**: Navigate to the dedicated page
   ```
   http://localhost:5000/broken_wrappers
   ```

3. **Results Table**: Broken wrappers are highlighted with red badges

### API Endpoint

Get broken wrapper statistics:
```bash
curl http://localhost:5000/api/broken_wrappers
```

Response format:
```json
{
  "total_broken_wrappers": 15,
  "total_ads": 1000,
  "broken_percentage": 1.5,
  "unique_broken_urls": 3,
  "broken_urls": [
    {
      "url": "https://broken-ad-server.com/vast",
      "occurrences": 10,
      "first_seen": "2024-01-15 10:30:00",
      "last_seen": "2024-01-20 15:45:00"
    }
  ]
}
```

### Testing

Run the test script to verify functionality:
```bash
python test_broken_wrapper.py
```

## Example Scenarios

### Scenario 1: Direct Empty VAST
```
VAST URL → <VAST status="NO_AD"/>
```
**Result**: Detected as broken wrapper

### Scenario 2: Wrapper Chain to Empty VAST
```
VAST URL → Wrapper → Wrapper → <VAST status="NO_AD"/>
```
**Result**: Detected with full wrapper chain tracked

### Scenario 3: Wrapper with No Ads
```
VAST URL → Wrapper → <VAST><!-- No Ad elements --></VAST>
```
**Result**: Detected as broken wrapper

## Integration with Monitoring

### Webhook Integration
You can integrate the API endpoint with monitoring systems:

```python
import requests
import json

def check_broken_wrappers():
    response = requests.get("http://localhost:5000/api/broken_wrappers")
    data = response.json()
    
    if data['broken_percentage'] > 5.0:  # Alert if >5% broken
        # Send alert to monitoring system
        send_alert(f"High broken wrapper rate: {data['broken_percentage']}%")
    
    # Check for new broken URLs
    for broken_url in data['broken_urls']:
        if is_new_broken_url(broken_url['url']):
            send_alert(f"New broken wrapper detected: {broken_url['url']}")
```

### Email Alerts
```python
def send_broken_wrapper_alert(broken_urls):
    subject = "Broken VAST Wrapper Alert"
    body = f"""
    The following VAST wrapper URLs are returning empty responses:
    
    {chr(10).join([f"- {url}" for url in broken_urls])}
    
    Please investigate these endpoints as they may be causing ad serving issues.
    """
    send_email(subject, body)
```

## Configuration

### Database Migration
The system automatically adds the required columns when first run:
- `broken_wrapper_url`: Stores the broken URL
- `wrapper_chain`: Stores the wrapper chain as JSON

### Customization
You can modify the detection logic in `parser_1.py`:
- Adjust timeout values for URL fetching
- Modify the criteria for what constitutes a "broken" response
- Add additional status codes or patterns to detect

## Troubleshooting

### Common Issues

1. **False Positives**: Some legitimate VAST responses may not contain ads
   - Solution: Review the detection logic and adjust as needed

2. **Timeout Issues**: Slow responding URLs may be marked as broken
   - Solution: Increase timeout values in the parser

3. **Database Errors**: Schema migration issues
   - Solution: Check database permissions and ensure proper SQLite setup

### Debug Mode
Enable debug logging by setting the Flask app to debug mode:
```python
app.run(debug=True)
```

## Future Enhancements

- **Email Notifications**: Automatic email alerts for new broken wrappers
- **Webhook Support**: Real-time notifications to external systems
- **Historical Analysis**: Trend analysis of broken wrapper patterns
- **Auto-Retry Logic**: Automatic retry of failed wrapper URLs
- **Performance Metrics**: Response time tracking for wrapper URLs

## Support

For issues or questions about the broken wrapper detection functionality:
1. Check the logs for detailed error messages
2. Verify the database schema is properly updated
3. Test with known working VAST URLs first
4. Review the wrapper chain information for debugging
