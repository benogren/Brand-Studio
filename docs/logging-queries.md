# Cloud Logging Queries for Brand Studio

This document contains useful Cloud Logging queries for debugging and monitoring the AI Brand Studio application.

## Overview

All Brand Studio agents log structured data to Google Cloud Logging with the following fields:
- `agent_name`: Name of the agent (orchestrator, name_generator, validation_agent, etc.)
- `action_type`: Type of action (initialize, generate, validate, etc.)
- `session_id`: Session identifier for correlation
- `timestamp`: UTC timestamp
- `duration_ms`: Time taken for the action (if applicable)
- `inputs`: Input parameters
- `outputs`: Output results
- `metadata`: Additional context

## Quick Start

1. **Open Cloud Logging Console:**
   ```
   https://console.cloud.google.com/logs/query?project=YOUR_PROJECT_ID
   ```

2. **Select the log name:**
   - Log name: `brand-studio-agents`

3. **Use the queries below to filter and analyze logs**

## Common Queries

### 1. View All Brand Studio Logs

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
```

**Use case:** See all logs from the Brand Studio application

---

### 2. Filter by Agent

**Orchestrator Logs:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.agent_name="orchestrator"
```

**Name Generator Logs:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.agent_name="name_generator"
```

**Validation Agent Logs:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.agent_name="validation_agent"
```

**SEO Agent Logs:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.agent_name="seo_agent"
```

**Story Agent Logs:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.agent_name="story_agent"
```

---

### 3. Filter by Session ID

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.session_id="SESSION_ID_HERE"
```

**Use case:** Track all actions in a specific user session

---

### 4. View Only Errors

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
severity>=ERROR
```

**Use case:** Debug production issues and failures

---

### 5. View Errors for Specific Agent

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.agent_name="name_generator"
severity>=ERROR
```

**Use case:** Isolate errors to a specific agent

---

### 6. View Agent Actions (Excludes Init)

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.action_type!="initialize"
```

**Use case:** See actual work being performed, not just initialization

---

### 7. Track Performance (Slow Actions)

**Actions taking longer than 5 seconds:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.duration_ms>5000
```

**Actions taking longer than 10 seconds:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.duration_ms>10000
```

**Use case:** Identify performance bottlenecks

---

### 8. View Metrics Only

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.metric_name:*
```

**Use case:** See performance metrics and counters

---

### 9. Track Complete Workflow

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.session_id="SESSION_ID_HERE"
timestamp>="2025-01-01T00:00:00Z"
timestamp<="2025-01-02T00:00:00Z"
```

**Use case:** Debug a specific workflow execution with time bounds

---

### 10. Count Actions by Agent

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.action_type:*
| group by jsonPayload.agent_name
| count
```

**Use case:** Understand agent usage patterns

---

### 11. Average Response Time by Agent

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.duration_ms>0
| group by jsonPayload.agent_name
| avg jsonPayload.duration_ms
```

**Use case:** Monitor agent performance over time

---

### 12. Recent Errors (Last 24 Hours)

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
severity>=ERROR
timestamp>="2025-01-01T00:00:00Z"
```

**Use case:** Check for recent production issues

---

### 13. Filter by Action Type

**Name Generation Actions:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.action_type="generate"
```

**Validation Actions:**
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.action_type="validate"
```

---

### 14. View Stack Traces for Errors

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
severity>=ERROR
jsonPayload.stack_trace:*
```

**Use case:** Debug exceptions with full context

---

### 15. Monitor Initialization Events

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.action_type="initialize"
```

**Use case:** Track agent startup and configuration

---

## Advanced Queries

### Find Sessions with Errors

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
severity>=ERROR
| group by jsonPayload.session_id
```

### Agent Action Timeline

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.session_id="SESSION_ID_HERE"
| order by timestamp asc
```

### Performance Percentiles

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
jsonPayload.duration_ms>0
| percentile jsonPayload.duration_ms, 50, 95, 99
```

---

## Creating Saved Queries

1. Run a query in Cloud Logging Console
2. Click "Save Query" button
3. Give it a descriptive name (e.g., "Brand Studio Errors - Last 7 Days")
4. Access saved queries from the left sidebar

---

## Setting Up Alerts

You can create alerts based on these queries:

### Example: Alert on High Error Rate

1. Go to Cloud Monitoring → Alerting
2. Create new alert policy
3. Add condition:
   - Resource type: Global
   - Metric: Log-based metric
   - Filter: Use error query above
   - Threshold: > 5 errors in 5 minutes
4. Configure notifications (email, Slack, PagerDuty, etc.)

### Example: Alert on Slow Performance

1. Create alert policy
2. Add condition:
   - Filter: `jsonPayload.duration_ms > 30000`
   - Threshold: > 3 slow requests in 10 minutes
3. Configure notifications

---

## Log Retention

- **Default retention:** 30 days
- **Extended retention:** Configure in Cloud Logging → Log Storage → Create bucket

---

## Tips for Effective Debugging

1. **Always include session_id** when debugging a specific workflow
2. **Use time ranges** to narrow down issues to specific time periods
3. **Check both INFO and ERROR** severity levels for context
4. **Look for patterns** in error_type and agent_name fields
5. **Use stack_trace** field to identify exact failure points
6. **Monitor duration_ms** to identify performance regressions

---

## Environment-Specific Queries

### Production Logs Only

Add environment label if configured:
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
labels.environment="production"
```

### Development Logs Only

```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/brand-studio-agents"
labels.environment="development"
```

---

## Export Logs

To export logs for analysis:

1. Run your query in Cloud Logging Console
2. Click "Actions" → "Export logs"
3. Choose destination:
   - BigQuery (for SQL analysis)
   - Cloud Storage (for archival)
   - Pub/Sub (for streaming)

---

## Related Documentation

- [Cloud Logging Query Language](https://cloud.google.com/logging/docs/view/logging-query-language)
- [Structured Logging Best Practices](https://cloud.google.com/logging/docs/structured-logging)
- [Log-based Metrics](https://cloud.google.com/logging/docs/logs-based-metrics)

---

## Support

For issues with logging setup or queries, check:
1. `src/infrastructure/logging.py` - Logging implementation
2. Agent files in `src/agents/` - Integration points
3. This documentation file for query examples
