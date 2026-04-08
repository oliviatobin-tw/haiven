// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { List, Typography } from "antd";

const Citations = ({ citations }) => {
  if (!citations || !Array.isArray(citations) || citations.length === 0) {
    return null;
  }

  return (
    <div className="citations-section">
      <Typography.Title level={5} className="!mt-0">
        Sources
      </Typography.Title>
      <List
        size="small"
        itemLayout="horizontal"
        dataSource={citations}
        className="text-xs"
        renderItem={(citation) => {
          // Handle both string URLs and object citations
          const url = typeof citation === "string" ? citation : citation.url;

          if (!url) return null;

          return (
            <List.Item className="py-[2px]">
              <ul className="list-disc m-0 pl-5">
                <li>
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs leading-[1.2]"
                  >
                    {url}
                  </a>
                </li>
              </ul>
            </List.Item>
          );
        }}
      />
    </div>
  );
};

export default Citations;
