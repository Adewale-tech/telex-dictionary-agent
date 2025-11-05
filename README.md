## Telex Workflow Configuration

This agent uses the following workflow configuration:

- **Category**: Education
- **Type**: A2A Protocol
- **Endpoint**: `/a2a/message`
- **Commands**: `define`, `meaning`, `help`
- **Capabilities**: Definitions, examples, synonyms, part of speech

### Workflow JSON

The complete workflow configuration can be found in `workflows/smartdict-workflow.json`.

To import into Telex:
1. Copy the workflow JSON
2. Go to Telex.im agent settings
3. Import or paste the workflow configuration
4. Update the URL to your deployed endpoint
5. Save and activate