-- Dapr State Management用テーブル（PostgreSQL）
-- Dapr公式の推奨スキーマに準拠

CREATE TABLE IF NOT EXISTS state_store (
    key text PRIMARY KEY,
    value jsonb NOT NULL,
    insert_date timestamptz DEFAULT now(),
    update_date timestamptz DEFAULT now()
);

-- キーの一意性を保証し、値はJSON形式で保存
-- DaprのPostgreSQLコンポーネント設定で"tableName": "state_store"と指定してください
