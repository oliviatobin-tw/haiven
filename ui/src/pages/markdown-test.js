// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import MarkdownRenderer from "../app/_markdown_renderer";
import { Card, Input, Space, Typography, Divider, Button } from "antd";

const { TextArea } = Input;
const { Title, Text } = Typography;

const MarkdownDemo = () => {
  const [markdownText, setMarkdownText] = useState(
    `# Mermaid

This is an example of markdown content with embedded Mermaid diagrams.

## Basic Flowchart

\`\`\`mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
\`\`\`

## Regular markdown features

You can use all standard markdown features:

* **Bold text**
* *Italic text*
* [Links](https://mermaid.js.org/)
* And more...

## Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Perform action
    System->>System: Process action
    System-->>User: Return result
\`\`\`

## Regular code blocks still work

\`\`\`javascript
// This is a regular code block
function hello() {
  console.log("Hello world!");
}
\`\`\`

## Class Diagram

\`\`\`mermaid
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    class Dog {
        +fetch()
    }
    class Cat {
        +scratch()
    }
    Animal <|-- Dog
    Animal <|-- Cat
\`\`\`
`,
  );

  return (
    <div className="p-5 max-w-[1200px] mx-auto">
      <Title level={2}>Test Page</Title>
      <Text>This is a page to test our Markdown rendering component</Text>

      <Divider />

      <div className="flex flex-col gap-5">
        <Card title="Markdown Editor">
          <Space direction="vertical" className="w-full">
            <TextArea
              rows={12}
              value={markdownText}
              onChange={(e) => setMarkdownText(e.target.value)}
              placeholder="Enter markdown with Mermaid diagrams here..."
              className="font-mono"
            />
          </Space>
        </Card>

        <Card title="Rendered Output">
          <div className="p-5 bg-white rounded-[5px] overflow-auto">
            <MarkdownRenderer
              content={markdownText}
              mermaidConfig={{ theme: "default" }}
              markdownProps={{
                className: "markdown-content",
                // You can add more ReactMarkdown props here
              }}
            />
          </div>
        </Card>
      </div>

      <Divider />

      <Card title="How to Use">
        <Typography>
          <Title level={4}>Using Mermaid in Markdown</Title>
          <Text>
            To render a Mermaid diagram in our chats, the AI needs to have added
            a code block marked with "mermaid" as the language:
          </Text>

          <pre className="bg-[#f0f0f0] p-[10px] rounded-[5px]">
            {`\`\`\`mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
\`\`\``}
          </pre>
        </Typography>
      </Card>
    </div>
  );
};

export default MarkdownDemo;
