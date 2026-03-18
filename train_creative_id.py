import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# --- 1. Load and Prepare Data ---
df = pd.read_csv("vast_ads-6.csv")

drop_cols = [
    'title', 'duration', 'clickthrough', 'media_urls', 'created_at',
    'adomain', 'creative_hash', 'ssai_creative_id', 'ssaicreative_id',
    'ad_xml', 'ad_metadata_json', 'vast_url', 'initial_metadata_json'
]
df = df.drop(columns=drop_cols, errors='ignore')
df = df.dropna(subset=['creative_id'])

# Target encoding
creative_encoder = LabelEncoder()
df['creative_id'] = creative_encoder.fit_transform(df['creative_id'])
num_classes = len(creative_encoder.classes_)

# Separate numeric and categorical columns
categorical_cols = [c for c in df.columns if df[c].dtype == 'object' and c != 'creative_id']
numeric_cols = [c for c in df.columns if c not in categorical_cols + ['creative_id']]

# Label encode categorical columns
cat_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    cat_encoders[col] = le

# Scale numeric features
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# Prepare feature arrays
X_cat = df[categorical_cols].values.astype(np.int64) if categorical_cols else None
X_num = df[numeric_cols].values.astype(np.float32) if numeric_cols else None
y = df['creative_id'].values

# Train/val/test split
X_train_cat, X_temp_cat, y_train, y_temp = train_test_split(
    X_cat, y, test_size=0.3, random_state=42
)
X_val_cat, X_test_cat, y_val, y_test = train_test_split(
    X_temp_cat, y_temp, test_size=0.5, random_state=42
)

if X_num is not None:
    X_train_num, X_temp_num = train_test_split(X_num, test_size=0.3, random_state=42)
    X_val_num, X_test_num = train_test_split(X_temp_num, test_size=0.5, random_state=42)
else:
    X_train_num = X_val_num = X_test_num = None

# --- 2. Dataset Class ---
class TabularDataset(Dataset):
    def __init__(self, X_cat, X_num, y):
        self.X_cat = torch.tensor(X_cat, dtype=torch.long) if X_cat is not None else None
        self.X_num = torch.tensor(X_num, dtype=torch.float32) if X_num is not None else None
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        cat = self.X_cat[idx] if self.X_cat is not None else None
        num = self.X_num[idx] if self.X_num is not None else None
        return cat, num, self.y[idx]

train_dataset = TabularDataset(X_train_cat, X_train_num, y_train)
val_dataset = TabularDataset(X_val_cat, X_val_num, y_val)
test_dataset = TabularDataset(X_test_cat, X_test_num, y_test)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)
test_loader = DataLoader(test_dataset, batch_size=32)

# --- 3. Transformer Model (Smaller + Regularized) ---
class TransformerTabular(nn.Module):
    def __init__(self, cat_cardinalities, num_features, d_model=64, nhead=4, num_layers=2, num_classes=10):
        super().__init__()
        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(cardinality, min(50, (cardinality + 1) // 2))
            for cardinality in cat_cardinalities
        ])
        cat_emb_dim = sum(emb.embedding_dim for emb in self.cat_embeddings)

        # Linear layer for numeric features
        self.num_linear = nn.Linear(num_features, d_model // 2) if num_features > 0 else None
        total_features = cat_emb_dim + (d_model // 2 if num_features > 0 else 0)
        self.input_linear = nn.Linear(total_features, d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, batch_first=True, dropout=0.4
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.fc = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x_cat, x_num):
        if x_cat is not None:
            cat_embs = [emb(x_cat[:, i]) for i, emb in enumerate(self.cat_embeddings)]
            cat_embs = torch.cat(cat_embs, dim=1)
        else:
            cat_embs = torch.zeros((x_num.size(0), 0), device=x_num.device)

        num_emb = self.num_linear(x_num) if self.num_linear is not None else torch.zeros((x_cat.size(0), 0), device=x_cat.device)
        x = torch.cat([cat_embs, num_emb], dim=1)

        x = self.input_linear(x).unsqueeze(1)
        x = self.transformer(x)
        x = x.mean(dim=1)
        return self.fc(x)

cat_cardinalities = [len(cat_encoders[col].classes_) for col in categorical_cols]
num_features = len(numeric_cols)
model = TransformerTabular(cat_cardinalities, num_features, num_classes=num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# --- 4. Training with Early Stopping ---
best_val_loss = float('inf')
patience = 5
patience_counter = 0
EPOCHS = 50

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for cat_batch, num_batch, y_batch in train_loader:
        optimizer.zero_grad()
        outputs = model(cat_batch, num_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # Validation
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for cat_batch, num_batch, y_batch in val_loader:
            outputs = model(cat_batch, num_batch)
            val_loss += criterion(outputs, y_batch).item()

    avg_train_loss = total_loss / len(train_loader)
    avg_val_loss = val_loss / len(val_loader)
    print(f"Epoch {epoch+1}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        torch.save(model.state_dict(), "creative_model_best.pth")
        print("  ** Best model saved **")
        patience_counter = 0
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print("Early stopping triggered!")
            break

# --- 5. Evaluate on Test Set ---
model.load_state_dict(torch.load("creative_model_best.pth"))
model.eval()
correct, total = 0, 0
with torch.no_grad():
    for cat_batch, num_batch, y_batch in test_loader:
        preds = model(cat_batch, num_batch).argmax(dim=1)
        correct += (preds == y_batch).sum().item()
        total += y_batch.size(0)
print(f"Test Accuracy: {100 * correct / total:.2f}%")

# --- 6. Save Encoders and Scaler ---
joblib.dump(creative_encoder, "creative_encoder.pkl")
joblib.dump(cat_encoders, "cat_encoders.pkl")
joblib.dump(scaler, "numeric_scaler.pkl")
joblib.dump((categorical_cols, numeric_cols), "features.pkl")
print("Model and encoders saved.")




#!/usr/bin/env python3
import asyncio
import os
from typing import Any, Dict, List, Optional
import json
from github import Github
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Load environment variables
load_dotenv()

class GitHubMCPServer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.github = Github(self.github_token)
        self.server = Server("github-mcp")
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="list_repositories",
                    description="List user's GitHub repositories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "per_page": {
                                "type": "integer",
                                "description": "Number of repositories per page (max 100)",
                                "default": 30
                            },
                            "type": {
                                "type": "string",
                                "description": "Type of repositories (all, owner, member)",
                                "enum": ["all", "owner", "member"],
                                "default": "owner"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_repository_info",
                    description="Get detailed information about a specific repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"}
                        },
                        "required": ["owner", "repo"]
                    }
                ),
                Tool(
                    name="read_file",
                    description="Read the contents of a file from a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "path": {"type": "string", "description": "File path"},
                            "branch": {"type": "string", "description": "Branch name", "default": "main"}
                        },
                        "required": ["owner", "repo", "path"]
                    }
                ),
                Tool(
                    name="list_directory",
                    description="List contents of a directory in a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "path": {"type": "string", "description": "Directory path", "default": ""},
                            "branch": {"type": "string", "description": "Branch name", "default": "main"}
                        },
                        "required": ["owner", "repo"]
                    }
                ),
                Tool(
                    name="search_code",
                    description="Search for code in repositories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "owner": {"type": "string", "description": "Limit search to specific owner (optional)"},
                            "repo": {"type": "string", "description": "Limit search to specific repo (optional)"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="list_issues",
                    description="List issues for a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                            "per_page": {"type": "integer", "default": 30}
                        },
                        "required": ["owner", "repo"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            try:
                if name == "list_repositories":
                    return await self._list_repositories(arguments)
                elif name == "get_repository_info":
                    return await self._get_repository_info(arguments)
                elif name == "read_file":
                    return await self._read_file(arguments)
                elif name == "list_directory":
                    return await self._list_directory(arguments)
                elif name == "search_code":
                    return await self._search_code(arguments)
                elif name == "list_issues":
                    return await self._list_issues(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _list_repositories(self, args: Dict[str, Any]) -> List[types.TextContent]:
        per_page = args.get('per_page', 30)
        repo_type = args.get('type', 'owner')
        
        user = self.github.get_user()
        repos = user.get_repos(type=repo_type)
        
        repo_list = []
        count = 0 
        for repo in repos:
            if count >= per_page:
                break
            repo_info = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "url": repo.html_url
            }
            repo_list.append(repo_info)
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(repo_list, indent=2)
        )]

    async def _get_repository_info(self, args: Dict[str, Any]) -> List[types.TextContent]:
        repo = self.github.get_repo(f"{args['owner']}/{args['repo']}")
        
        info = {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": repo.private,
            "fork": repo.fork,
            "language": repo.language,
            "size": repo.size,
            "stargazers_count": repo.stargazers_count,
            "watchers_count": repo.watchers_count,
            "forks_count": repo.forks_count,
            "open_issues_count": repo.open_issues_count,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
            "clone_url": repo.clone_url,
            "html_url": repo.html_url,
            "topics": repo.get_topics(),
            "license": repo.license.name if repo.license else None,
            "default_branch": repo.default_branch
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(info, indent=2)
        )]

    async def _read_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        repo = self.github.get_repo(f"{args['owner']}/{args['repo']}")
        branch = args.get('branch', 'main')
        
        try:
            file_content = repo.get_contents(args['path'], ref=branch)
            content = file_content.decoded_content.decode('utf-8')
            
            return [types.TextContent(
                type="text",
                text=f"File: {args['path']}\nBranch: {branch}\n\n{content}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error reading file {args['path']}: {str(e)}"
            )]

    async def _list_directory(self, args: Dict[str, Any]) -> List[types.TextContent]:
        repo = self.github.get_repo(f"{args['owner']}/{args['repo']}")
        path = args.get('path', '')
        branch = args.get('branch', 'main')
        
        try:
            contents = repo.get_contents(path, ref=branch)
            if not isinstance(contents, list):
                contents = [contents]
            
            items = []
            for item in contents:
                items.append({
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size,
                    "download_url": item.download_url
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps(items, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error listing directory {path}: {str(e)}"
            )]

    async def _search_code(self, args: Dict[str, Any]) -> List[types.TextContent]:
        query = args['query']
        owner = args.get('owner')
        repo = args.get('repo')
        
        # Build search query
        search_query = query
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        try:
            results = self.github.search_code(search_query)
            
            search_results = []
            for result in results[:10]:  # Limit to first 10 results
                search_results.append({
                    "repository": result.repository.full_name,
                    "path": result.path,
                    "name": result.name,
                    "html_url": result.html_url,
                    "score": result.score
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps(search_results, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching code: {str(e)}"
            )]

    async def _list_issues(self, args: Dict[str, Any]) -> List[types.TextContent]:
        repo = self.github.get_repo(f"{args['owner']}/{args['repo']}")
        state = args.get('state', 'open')
        per_page = args.get('per_page', 30)
        
        try:
            issues = repo.get_issues(state=state, per_page=per_page)
            
            issue_list = []
            for issue in issues:
                if not issue.pull_request:  # Exclude pull requests
                    issue_info = {
                        "number": issue.number,
                        "title": issue.title,
                        "state": issue.state,
                        "user": issue.user.login,
                        "created_at": issue.created_at.isoformat() if issue.created_at else None,
                        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                        "labels": [label.name for label in issue.labels],
                        "assignees": [assignee.login for assignee in issue.assignees],
                        "html_url": issue.html_url,
                        "body": issue.body[:200] + "..." if issue.body and len(issue.body) > 200 else issue.body
                    }
                    issue_list.append(issue_info)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(issue_list, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error listing issues: {str(e)}"
            )]

    async def run(self):
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="github-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    server = GitHubMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())