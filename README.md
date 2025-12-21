# Dapr + FastAPI + PostgreSQL State Management Demo

DaprのステートマネジメントAPIを使用して、Azure Database for PostgreSQL（Entra ID認証）にデータを保存・取得するFastAPIアプリケーションです。

## 機能

- **POST /state**: キーと値をPostgreSQLに保存
- **GET /state/{key}**: キーで値を取得
- **DELETE /state/{key}**: キーで値を削除
- **GET /**: エンドポイント一覧
- **GET /health**: ヘルスチェック

## ローカル実行（Dapr CLI使用）

### 前提条件

- Python 3.11+
- Dapr CLI
- Docker（ローカルテスト用PostgreSQL）

### 手順

1. 依存関係をインストール:

```bash
pip install -r requirements.txt
```

2. Dapr経由でアプリを起動:

```bash
dapr run --app-id fastapi-demo --app-port 8000 --dapr-http-port 3500 -- python app.py
```

3. APIをテスト:

```bash
# 状態を保存
curl -X POST http://localhost:8000/state -H "Content-Type: application/json" -d '{"key":"user1","value":"John Doe"}'

# 状態を取得
curl http://localhost:8000/state/user1

# 状態を削除
curl -X DELETE http://localhost:8000/state/user1
```

## Azure Container Appsへのデプロイ

### Dockerイメージをビルド＆プッシュ

```bash
# Azure Container Registryにログイン
az acr login --name <your-acr-name>

# イメージをビルド
docker build -t <your-acr-name>.azurecr.io/fastapi-dapr-demo:latest .

# イメージをプッシュ
docker push <your-acr-name>.azurecr.io/fastapi-dapr-demo:latest
```

### Container Appを作成（Bicep例）

```bicep
resource fastapiApp 'Microsoft.App/containerApps@2025-02-02-preview' = {
  name: 'fastapi-dapr-demo'
  location: location
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
      }
      dapr: {
        enabled: true
        appId: 'fastapi-demo'
        appPort: 8000
        appProtocol: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'fastapi-dapr-demo'
          image: '<your-acr-name>.azurecr.io/fastapi-dapr-demo:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '<managed-identity-resource-id>': {}
    }
  }
}
```

## 環境変数

- `DAPR_HTTP_PORT`: Dapr HTTPポート（デフォルト: 3500）

## Daprコンポーネント設定

このアプリは、`auth-psql`という名前のDaprステートストアコンポーネントを使用します。
Bicepで定義したコンポーネント設定が自動的に適用されます。

## トラブルシューティング

- **Daprに接続できない**: DAPR_HTTP_PORT環境変数を確認
- **PostgreSQL認証エラー**: マネージドIDがPostgreSQLに登録されているか確認
- **状態が保存されない**: Daprコンポーネントが正しくデプロイされているか確認
