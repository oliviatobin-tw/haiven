// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import {
  Button,
  Card,
  Table,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Typography,
  Space,
  Tag,
  Alert,
  Tooltip,
  Divider,
} from "antd";
import {
  RiKeyLine,
  RiAddLine,
  RiDeleteBin6Line,
  RiEyeLine,
  RiEyeOffLine,
  RiFileCopyLine,
  RiInformationLine,
} from "react-icons/ri";
import { toast } from "react-toastify";
import {
  getApiKeys,
  generateApiKey,
  revokeApiKey,
  getApiKeyUsage,
} from "../app/_boba_api";
import { FEATURES } from "../app/feature_toggle";

const { Title, Text, Paragraph } = Typography;

export default function ApiKeys({ featureToggleConfig = {} }) {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generateModalVisible, setGenerateModalVisible] = useState(false);
  const [keyModalVisible, setKeyModalVisible] = useState(false);
  const [generatedKey, setGeneratedKey] = useState(null);
  const [keyVisible, setKeyVisible] = useState(false);
  const [usage, setUsage] = useState(null);
  const [form] = Form.useForm();
  const [expiryDays, setExpiryDays] = useState(30);
  const [generateError, setGenerateError] = useState(null);

  // Check if API key auth feature is enabled
  const isApiKeyAuthEnabled =
    featureToggleConfig[FEATURES.API_KEY_AUTH_UI] === true;

  useEffect(() => {
    if (isApiKeyAuthEnabled) {
      loadApiKeys();
      loadUsage();
    } else {
      setLoading(false);
    }
  }, [isApiKeyAuthEnabled]);

  const loadApiKeys = () => {
    setLoading(true);
    getApiKeys(
      (data) => {
        setApiKeys(data.keys || []);
        setLoading(false);
      },
      (error) => {
        console.error("Error loading API keys:", error);
        message.error("Failed to load API keys");
        setLoading(false);
      },
    );
  };

  const loadUsage = () => {
    getApiKeyUsage(
      (data) => {
        setUsage(data);
      },
      (error) => {
        console.error("Error loading usage:", error);
      },
    );
  };

  const handleGenerateKey = async (values) => {
    setGenerateError(null); // reset error on new attempt
    try {
      generateApiKey(
        values.name,
        (data) => {
          setGeneratedKey(data);
          setKeyModalVisible(true);
          setGenerateModalVisible(false);
          form.resetFields();
          setExpiryDays(30); // reset to default
          setGenerateError(null);
          loadApiKeys();
          loadUsage();
          message.success("API key generated successfully!");
        },
        (error) => {
          console.error("Error generating API key:", error);
          setGenerateError(error.message || "Failed to generate API key");
          // Do not close modal
        },
        expiryDays,
      );
    } catch (error) {
      console.error("Error generating API key:", error);
      setGenerateError("Failed to generate API key");
    }
  };

  const handleRevokeKey = (keyHash, keyName) => {
    revokeApiKey(
      keyHash,
      (data) => {
        message.success(`API key "${keyName}" revoked successfully`);
        loadApiKeys();
        loadUsage();
      },
      (error) => {
        console.error("Error revoking API key:", error);
        message.error(`Failed to revoke API key: ${error.message}`);
      },
    );
  };

  const copyToClipboard = (text) => {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        message.success("Copied to clipboard");
      })
      .catch(() => {
        message.error("Failed to copy to clipboard");
      });
  };

  const formatDateTime = (isoString) => {
    if (!isoString) return "Never";
    return new Date(isoString).toLocaleString();
  };

  const getKeyStatus = (expiresAt) => {
    if (!expiresAt) return <Tag color="red">Invalid</Tag>;
    const now = new Date();
    const expires = new Date(expiresAt);
    const daysUntilExpiry = Math.ceil((expires - now) / (1000 * 60 * 60 * 24));

    if (daysUntilExpiry < 0) {
      return <Tag color="red">Expired</Tag>;
    } else if (daysUntilExpiry < 30) {
      return <Tag color="orange">Expires in {daysUntilExpiry} days</Tag>;
    } else {
      return <Tag color="green">Active</Tag>;
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: "Status",
      dataIndex: "expires_at",
      key: "status",
      render: (expiresAt) => getKeyStatus(expiresAt),
    },
    {
      title: "Created",
      dataIndex: "created_at",
      key: "created_at",
      render: (text) => formatDateTime(text),
    },
    {
      title: "Expires",
      dataIndex: "expires_at",
      key: "expires_at",
      render: (text) => formatDateTime(text),
    },
    {
      title: "Last Used",
      dataIndex: "last_used",
      key: "last_used",
      render: (text) => formatDateTime(text),
    },
    {
      title: "Usage Count",
      dataIndex: "usage_count",
      key: "usage_count",
      render: (count) => <Text>{count || 0}</Text>,
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
        <Space size="middle">
          <Popconfirm
            title="Are you sure you want to revoke this API key?"
            description="This action cannot be undone and will immediately invalidate the key."
            onConfirm={() => handleRevokeKey(record.key_hash, record.name)}
            okText="Yes, Revoke"
            cancelText="Cancel"
            okButtonProps={{ danger: true }}
          >
            <Button
              danger
              size="small"
              icon={<RiDeleteBin6Line />}
              title="Revoke API Key"
            >
              Revoke
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Show disabled message if feature is not enabled
  if (!isApiKeyAuthEnabled) {
    return (
      <div className="p-6 max-w-[1200px] mx-auto">
        <div className="mb-6">
          <Title level={2}>
            <RiKeyLine className="mr-2" />
            API Key Management
          </Title>
          <Alert
            message="Feature Disabled"
            description="API key authentication is currently disabled. This feature is not available in this environment."
            type="info"
            showIcon
            className="mb-4"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-[1200px] mx-auto">
      <div className="mb-6">
        <Title level={2}>
          <RiKeyLine className="mr-2" />
          API Key Management
        </Title>
        <Paragraph>
          Manage your API keys for programmatic access to Haiven. API keys
          provide secure authentication for integrations like MCP servers, CLI
          tools, and other applications. All API keys are valid for 24 hours
          from the time of generation for enhanced security.
        </Paragraph>
      </div>

      {/* Usage Statistics */}
      {usage && (
        <Card className="mb-6">
          <Title level={4}>Usage Statistics</Title>
          <Space size="large">
            <div>
              <Text type="secondary">Total API Keys</Text>
              <br />
              <Text className="text-2xl font-bold">
                {usage.total_keys}
              </Text>
            </div>
            <div>
              <Text type="secondary">Total Usage</Text>
              <br />
              <Text className="text-2xl font-bold">
                {usage.total_usage}
              </Text>
            </div>
            <div>
              <Text type="secondary">Last Used</Text>
              <br />
              <Text className="text-base">
                {formatDateTime(usage.most_recent_usage)}
              </Text>
            </div>
          </Space>
        </Card>
      )}

      {/* Action Bar */}
      <div className="mb-6 flex justify-between items-center">
        <Title level={4} className="!m-0">
          Your API Keys
        </Title>
        <Button
          type="primary"
          icon={<RiAddLine />}
          onClick={() => setGenerateModalVisible(true)}
        >
          Generate New API Key
        </Button>
      </div>

      {/* API Keys Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={apiKeys}
          loading={loading}
          rowKey="key_hash"
          pagination={false}
          locale={{
            emptyText: (
              <div className="text-center p-12">
                <RiKeyLine
                  className="text-[48px] text-[#d9d9d9] mb-4"
                />
                <div>No API keys found</div>
                <div className="mt-2">
                  <Button
                    type="primary"
                    onClick={() => setGenerateModalVisible(true)}
                  >
                    Generate Your First API Key
                  </Button>
                </div>
              </div>
            ),
          }}
        />
      </Card>

      {/* Generate API Key Modal */}
      <Modal
        title="Generate New API Key"
        open={generateModalVisible}
        onCancel={() => {
          setGenerateModalVisible(false);
          setGenerateError(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
        destroyOnClose
      >
        {generateError && (
          <Alert
            message="Error"
            description={generateError}
            type="error"
            showIcon
            className="mb-4"
          />
        )}
        <Form form={form} layout="vertical" onFinish={handleGenerateKey}>
          <Form.Item
            label="API Key Name"
            name="name"
            rules={[
              {
                required: true,
                message: "Please enter a name for the API key",
              },
            ]}
          >
            <Input placeholder="e.g. My Integration Key" maxLength={64} />
          </Form.Item>
          <Form.Item
            label={
              <span>
                Expiry (days)
                <Tooltip title="API keys can be valid for 1 to 30 days. Default is 30.">
                  <RiInformationLine className="ml-1.5" />
                </Tooltip>
              </span>
            }
            required
            validateStatus={expiryDays < 1 || expiryDays > 30 ? "error" : ""}
            help={
              expiryDays < 1 || expiryDays > 30
                ? "Expiry must be between 1 and 30 days"
                : ""
            }
          >
            <Input
              type="number"
              min={1}
              max={30}
              value={expiryDays}
              onChange={(e) => {
                let val = parseInt(e.target.value, 10);
                if (isNaN(val)) val = 30;
                setExpiryDays(val);
              }}
              className="w-[120px]"
            />
          </Form.Item>

          <Alert
            message="Validity Period"
            description="API keys are valid for 24 hours from the time of generation for security purposes."
            type="info"
            showIcon
            className="mb-4"
          />

          <Alert
            message="Security Notice"
            description="The API key will be shown only once after generation. Make sure to copy and store it securely."
            type="warning"
            showIcon
            className="mb-4"
          />

          <Form.Item className="!mb-0">
            <Space>
              <Button type="primary" htmlType="submit" icon={<RiKeyLine />}>
                Generate API Key
              </Button>
              <Button
                onClick={() => {
                  setGenerateModalVisible(false);
                  setGenerateError(null);
                  form.resetFields();
                }}
              >
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Generated API Key Modal */}
      <Modal
        title="API Key Generated Successfully"
        open={keyModalVisible}
        onCancel={() => {
          setKeyModalVisible(false);
          setGeneratedKey(null);
          setKeyVisible(false);
        }}
        footer={[
          <Button
            key="close"
            onClick={() => {
              setKeyModalVisible(false);
              setGeneratedKey(null);
              setKeyVisible(false);
            }}
          >
            Close
          </Button>,
        ]}
        width={700}
      >
        {generatedKey && (
          <div>
            <Alert
              message="Important: Save Your API Key"
              description="This is the only time you'll be able to view this API key. Make sure to copy it to a secure location."
              type="error"
              showIcon
              className="mb-4"
            />

            <Space direction="vertical" className="w-full">
              <div>
                <Text strong>Name:</Text> {generatedKey.name}
              </div>
              <div>
                <Text strong>Expires:</Text> 24 hours from now
              </div>

              <Divider />

              <div>
                <Text strong>API Key:</Text>
                <div className="mt-2">
                  <Input.Group compact>
                    <Input
                      value={generatedKey.api_key}
                      readOnly
                      type={keyVisible ? "text" : "password"}
                      className="w-[calc(100%-80px)]"
                    />
                    <Button
                      icon={keyVisible ? <RiEyeOffLine /> : <RiEyeLine />}
                      onClick={() => setKeyVisible(!keyVisible)}
                      className="w-10"
                    />
                    <Button
                      icon={<RiFileCopyLine />}
                      onClick={() => copyToClipboard(generatedKey.api_key)}
                      className="w-10"
                    />
                  </Input.Group>
                </div>
              </div>

              <Divider />

              <div>
                <Title level={5}>Usage Examples:</Title>
                <Text code>export HAIVEN_API_KEY="YOUR_API_KEY_HERE"</Text>
                <br />
                <Text code>Authorization: Bearer YOUR_API_KEY_HERE</Text>
                <br />
                <Text code>X-API-Key: YOUR_API_KEY_HERE</Text>
              </div>

              <Alert
                message="Next Steps"
                description="Configure your MCP client or application to use this API key. See the documentation for specific integration instructions."
                type="info"
                showIcon
                icon={<RiInformationLine />}
              />
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
}
