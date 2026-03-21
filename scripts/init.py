"""
Initialization script for the Autonomous Multi-Agent Executor.

This script sets up the project structure, installs dependencies,
creates necessary directories, and configures the environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectInitializer:
    """Handles project initialization and setup."""
    
    def __init__(self, project_root: str = None):
        """Initialize the project initializer."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.required_dirs = [
            "app",
            "app/agents",
            "app/executor", 
            "app/tools",
            "app/models",
            "app/api",
            "tests",
            "scripts",
            "uploads",
            "logs"
        ]
        self.required_files = [
            ".env.example",
            ".gitignore",
            "requirements.txt",
            "README.md",
            "Dockerfile",
            "docker-compose.yml",
            "Makefile"
        ]
    
    def create_directory_structure(self) -> bool:
        """Create the required directory structure."""
        logger.info("Creating directory structure...")
        
        try:
            for dir_path in self.required_dirs:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {full_path}")
            
            logger.info("Directory structure created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directory structure: {str(e)}")
            return False
    
    def create_env_file(self) -> bool:
        """Create .env file from .env.example if it doesn't exist."""
        env_example_path = self.project_root / ".env.example"
        env_path = self.project_root / ".env"
        
        if env_path.exists():
            logger.info(".env file already exists")
            return True
        
        if not env_example_path.exists():
            logger.warning(".env.example file not found")
            return False
        
        try:
            shutil.copy2(env_example_path, env_path)
            logger.info("Created .env file from .env.example")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create .env file: {str(e)}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies from requirements.txt."""
        requirements_path = self.project_root / "requirements.txt"
        
        if not requirements_path.exists():
            logger.warning("requirements.txt not found")
            return False
        
        logger.info("Installing Python dependencies...")
        
        try:
            # Use pip to install requirements
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("Dependencies installed successfully")
                return True
            else:
                logger.error(f"Failed to install dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install dependencies: {str(e)}")
            return False
    
    def setup_git_repository(self) -> bool:
        """Initialize git repository if not already initialized."""
        git_dir = self.project_root / ".git"
        
        if git_dir.exists():
            logger.info("Git repository already initialized")
            return True
        
        logger.info("Initializing git repository...")
        
        try:
            # Initialize git repository
            subprocess.run(
                ["git", "init"],
                capture_output=True,
                cwd=self.project_root
            )
            
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                cwd=self.project_root
            )
            
            # Create initial commit
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: Autonomous Multi-Agent Executor setup"],
                capture_output=True,
                cwd=self.project_root
            )
            
            logger.info("Git repository initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize git repository: {str(e)}")
            return False
    
    def create_ui_directories(self) -> bool:
        """Create UI-related directories for frontend development."""
        ui_dirs = [
            "ui",
            "ui/src",
            "ui/public",
            "ui/components",
            "ui/pages",
            "ui/styles",
            "ui/utils"
        ]
        
        logger.info("Creating UI directories...")
        
        try:
            for dir_path in ui_dirs:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created UI directory: {full_path}")
            
            # Create basic UI files
            self._create_basic_ui_files()
            
            logger.info("UI directories created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create UI directories: {str(e)}")
            return False
    
    def _create_basic_ui_files(self) -> None:
        """Create basic UI files for the frontend."""
        ui_src_path = self.project_root / "ui" / "src"
        
        # Create package.json
        package_json = {
            "name": "autonomous-multi-agent-ui",
            "version": "0.1.0",
            "description": "Frontend UI for Autonomous Multi-Agent Executor",
            "main": "index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0",
                "axios": "^1.3.0",
                "antd": "^5.2.0",
                "@ant-design/icons": "^5.0.0",
                "react-scripts": "5.0.1"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        import json
        package_json_path = self.project_root / "ui" / "package.json"
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic React App.js
        app_js_content = '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, Typography } from 'antd';
import { RobotOutlined, SettingOutlined, DashboardOutlined } from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Agents from './pages/Agents';
import './App.css';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider theme="dark" width={250}>
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <Title level={4} style={{ color: 'white', margin: 0 }}>
              <RobotOutlined /> Agent Executor
            </Title>
          </div>
          <Menu theme="dark" mode="inline" defaultSelectedKeys={['dashboard']}>
            <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
              Dashboard
            </Menu.Item>
            <Menu.Item key="tasks" icon={<RobotOutlined />}>
              Tasks
            </Menu.Item>
            <Menu.Item key="agents" icon={<SettingOutlined />}>
              Agents
            </Menu.Item>
          </Menu>
        </Sider>
        
        <Layout>
          <Header style={{ background: '#fff', padding: '0 24px' }}>
            <Title level={3} style={{ margin: '16px 0' }}>Autonomous Multi-Agent Executor</Title>
          </Header>
          
          <Content style={{ margin: '24px', padding: '24px', background: '#fff' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/agents" element={<Agents />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
'''
        
        app_js_path = ui_src_path / "App.js"
        with open(app_js_path, 'w') as f:
            f.write(app_js_content)
        
        # Create basic index.js
        index_js_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
        
        index_js_path = ui_src_path / "index.js"
        with open(index_js_path, 'w') as f:
            f.write(index_js_content)
        
        # Create basic CSS files
        app_css_content = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

.ant-layout-sider .ant-menu {
  border-right: none;
}

.ant-layout-header {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
'''
        
        app_css_path = ui_src_path / "App.css"
        with open(app_css_path, 'w') as f:
            f.write(app_css_content)
        
        index_css_content = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
'''
        
        index_css_path = ui_src_path / "index.css"
        with open(index_css_path, 'w') as f:
            f.write(index_css_content)
        
        # Create basic page components
        pages_dir = ui_src_path / "pages"
        
        # Dashboard component
        dashboard_js_content = '''import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Progress } from 'antd';
import { RobotOutlined, CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

function Dashboard() {
  const [stats, setStats] = useState({
    totalAgents: 5,
    activeTasks: 3,
    completedTasks: 42,
    failedTasks: 2
  });
  
  const [recentTasks, setRecentTasks] = useState([
    {
      key: '1',
      id: 'task_001',
      type: 'Research & Write',
      status: 'completed',
      progress: 100,
      agent: 'researcher, writer'
    },
    {
      key: '2',
      id: 'task_002',
      type: 'Code Generation',
      status: 'running',
      progress: 65,
      agent: 'coder'
    },
    {
      key: '3',
      id: 'task_003',
      type: 'Data Analysis',
      status: 'pending',
      progress: 0,
      agent: 'researcher'
    }
  ]);

  const columns = [
    {
      title: 'Task ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const color = status === 'completed' ? 'green' : status === 'running' ? 'blue' : 'default';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      }
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress) => <Progress percent={progress} size="small" />
    },
    {
      title: 'Agent(s)',
      dataIndex: 'agent',
      key: 'agent',
    }
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Agents"
              value={stats.totalAgents}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active Tasks"
              value={stats.activeTasks}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Completed Tasks"
              value={stats.completedTasks}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Failed Tasks"
              value={stats.failedTasks}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>
      
      <Card title="Recent Tasks" size="large">
        <Table
          columns={columns}
          dataSource={recentTasks}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}

export default Dashboard;
'''
        
        dashboard_path = pages_dir / "Dashboard.js"
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_js_content)
        
        # Create placeholder components for other pages
        tasks_js_content = '''import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

function Tasks() {
  return (
    <Card>
      <Title level={2}>Tasks Management</Title>
      <p>Task management interface will be implemented here.</p>
    </Card>
  );
}

export default Tasks;
'''
        
        tasks_path = pages_dir / "Tasks.js"
        with open(tasks_path, 'w') as f:
            f.write(tasks_js_content)
        
        agents_js_content = '''import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

function Agents() {
  return (
    <Card>
      <Title level={2}>Agents Management</Title>
      <p>Agent management interface will be implemented here.</p>
    </Card>
  );
}

export default Agents;
'''
        
        agents_path = pages_dir / "Agents.js"
        with open(agents_path, 'w') as f:
            f.write(agents_js_content)
        
        # Create public/index.html
        public_dir = self.project_root / "ui" / "public"
        index_html_content = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Autonomous Multi-Agent Executor UI" />
    <title>Autonomous Multi-Agent Executor</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
'''
        
        index_html_path = public_dir / "index.html"
        with open(index_html_path, 'w') as f:
            f.write(index_html_content)
        
        logger.info("Basic UI files created successfully")
    
    def verify_setup(self) -> Dict[str, bool]:
        """Verify that the project setup is complete."""
        verification_results = {}
        
        # Check directories
        for dir_path in self.required_dirs:
            full_path = self.project_root / dir_path
            verification_results[f"dir_{dir_path}"] = full_path.exists() and full_path.is_dir()
        
        # Check files
        for file_name in self.required_files:
            file_path = self.project_root / file_name
            verification_results[f"file_{file_name}"] = file_path.exists() and file_path.is_file()
        
        # Check .env file
        env_path = self.project_root / ".env"
        verification_results["file_.env"] = env_path.exists()
        
        # Check UI directories
        ui_dirs = ["ui", "ui/src", "ui/public"]
        for dir_path in ui_dirs:
            full_path = self.project_root / dir_path
            verification_results[f"ui_dir_{dir_path}"] = full_path.exists() and full_path.is_dir()
        
        return verification_results
    
    def print_setup_summary(self) -> None:
        """Print a summary of the setup process."""
        verification_results = self.verify_setup()
        
        print("\\n" + "="*50)
        print("SETUP SUMMARY")
        print("="*50)
        
        all_good = True
        for item, status in verification_results.items():
            status_str = "✓" if status else "✗"
            item_name = item.replace("_", " ").title()
            print(f"{status_str} {item_name}")
            if not status:
                all_good = False
        
        print("\\n" + "="*50)
        if all_good:
            print("🎉 Setup completed successfully!")
            print("\\nNext steps:")
            print("1. Review and update .env file with your API keys")
            print("2. Run 'python -m uvicorn app.main:app --reload' to start the backend")
            print("3. Run 'cd ui && npm install && npm start' to start the frontend")
            print("4. Open http://localhost:3000 to access the UI")
        else:
            print("⚠️  Setup incomplete. Please check the items marked with ✗")
        
        print("="*50)
    
    def run_full_setup(self, create_ui: bool = True) -> bool:
        """Run the complete setup process."""
        logger.info("Starting full project setup...")
        
        steps = [
            ("Creating directory structure", self.create_directory_structure),
            ("Creating .env file", self.create_env_file),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up git repository", self.setup_git_repository)
        ]
        
        if create_ui:
            steps.append(("Creating UI directories", self.create_ui_directories))
        
        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            if not step_func():
                logger.error(f"Failed to complete step: {step_name}")
                return False
        
        logger.info("Setup completed successfully")
        return True


def main():
    """Main function to run the initialization script."""
    parser = argparse.ArgumentParser(description="Initialize Autonomous Multi-Agent Executor project")
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Skip UI creation"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing setup"
    )
    
    args = parser.parse_args()
    
    initializer = ProjectInitializer(args.project_root)
    
    if args.verify_only:
        initializer.print_setup_summary()
        return
    
    success = initializer.run_full_setup(create_ui=not args.no_ui)
    
    if success:
        initializer.print_setup_summary()
        sys.exit(0)
    else:
        logger.error("Setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
