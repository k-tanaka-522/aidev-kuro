# AgentDev Platform

マルチエージェント型システム開発プラットフォーム with Amazon Bedrock

## 概要

AgentDev Platformは、Amazon Bedrockを活用したマルチエージェント型のシステム開発プラットフォームです。PM、アーキテクト、セキュリティの3つのAIエージェントが協調して、プロジェクトの計画から実装まで自動化します。

## 技術スタック

### フロントエンド
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Zustand (状態管理)
- React Query (データフェッチング)

### バックエンド
- FastAPI (Python 3.11)
- DynamoDB (データベース)
- Amazon Bedrock Agents
- Amazon S3 (ファイルストレージ)

### インフラストラクチャ
- AWS CloudFormation
- ECS Fargate
- API Gateway
- AWS Cognito (認証)
- OpenSearch (検索)

## プロジェクト構造

```
├── cloudformation/          # CloudFormationテンプレート
│   ├── main.yaml           # メインスタック
│   ├── network/            # ネットワーク関連
│   ├── data/               # データストア関連
│   ├── security/           # セキュリティ関連
│   ├── compute/            # コンピュート関連
│   └── ai/                 # AI/ML関連
├── backend/                # FastAPIバックエンド
│   ├── app/
│   │   ├── api/v1/         # APIルーター
│   │   ├── models/         # データモデル
│   │   ├── services/       # ビジネスロジック
│   │   └── utils/          # ユーティリティ
│   └── requirements.txt
├── frontend/               # Reactフロントエンド
│   ├── src/
│   │   ├── components/     # UIコンポーネント
│   │   ├── pages/          # ページコンポーネント
│   │   ├── services/       # APIクライアント
│   │   └── stores/         # 状態管理
│   └── package.json
├── lambda/                 # Lambda関数
│   ├── agents/             # エージェント関連
│   ├── websocket/          # WebSocket関連
│   └── authorizer/         # 認証関連
└── agents/                 # エージェント設定
    ├── pm/                 # PMエージェント
    ├── architect/          # アーキテクトエージェント
    └── security/           # セキュリティエージェント
```

## セットアップ

### 前提条件

- AWS CLI v2
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### 環境変数

```bash
export AWS_REGION=us-east-1
export BEDROCK_REGION=us-east-1
export PROJECT_NAME=agentdev
export ENVIRONMENT=dev
```

### バックエンド起動

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンド起動

```bash
cd frontend
npm install
npm run dev
```

## API エンドポイント

### 認証
- `POST /api/v1/auth/login` - ログイン
- `POST /api/v1/auth/logout` - ログアウト

### プロジェクト管理
- `GET /api/v1/projects/` - プロジェクト一覧
- `POST /api/v1/projects/` - プロジェクト作成
- `GET /api/v1/projects/{id}` - プロジェクト詳細
- `PUT /api/v1/projects/{id}` - プロジェクト更新
- `DELETE /api/v1/projects/{id}` - プロジェクト削除

### エージェント管理
- `GET /api/v1/agents/` - エージェント一覧
- `POST /api/v1/agents/` - エージェント作成
- `GET /api/v1/agents/{id}` - エージェント詳細

### メッセージ・チャット
- `GET /api/v1/messages/channels` - チャンネル一覧
- `GET /api/v1/messages/{channel_id}` - メッセージ取得
- `POST /api/v1/messages/` - メッセージ送信

### 成果物管理
- `GET /api/v1/artifacts/` - 成果物一覧
- `POST /api/v1/artifacts/` - 成果物作成
- `GET /api/v1/artifacts/{id}` - 成果物詳細

## デプロイ

### CloudFormationスタックのデプロイ

```bash
# パラメータファイルを作成
aws cloudformation deploy \
  --template-file cloudformation/main.yaml \
  --stack-name agentdev-dev \
  --parameter-overrides \
    Environment=dev \
    ProjectName=agentdev \
  --capabilities CAPABILITY_NAMED_IAM
```

### Dockerでのデプロイ

```bash
# バックエンド
cd backend
docker build -t agentdev-backend .
docker run -p 8000:8000 agentdev-backend

# フロントエンド
cd frontend
docker build -t agentdev-frontend .
docker run -p 3000:3000 agentdev-frontend
```

## 機能

### 実装済み機能

- ✅ プロジェクト管理（CRUD操作）
- ✅ ユーザー認証（JWT + Cognito）
- ✅ DynamoDBデータストレージ
- ✅ RESTful API（FastAPI）
- ✅ レスポンシブWebUI（React）
- ✅ Bedrock Agents基本実装

### 今後の実装予定

- 🔄 WebSocketリアルタイム通信
- 🔄 エージェント間協調システム
- 🔄 成果物管理とバージョン管理
- 🔄 GitHub連携
- 🔄 検索・分析機能
- 🔄 監視・ログ機能

## 開発

### テスト実行

```bash
# バックエンドテスト
cd backend
pytest

# フロントエンドテスト
cd frontend
npm test
```

### リント・フォーマット

```bash
# バックエンド
cd backend
black .
flake8 .

# フロントエンド
cd frontend
npm run lint
```

## ライセンス

MIT License

## 作成者

- k-tanaka-522

## 参考資料

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)