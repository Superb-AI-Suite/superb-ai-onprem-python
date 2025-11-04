# 🚀 Superb AI On-premise Python SDK

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://i#### **📊 Data Management Workflow**
1. Start with [📁 Datasets](spb_onprem/datasets/README.md) - Create and organize your data collections
2. Then explore [📊 Data](spb_onprem/data/README.md) - Manage individual items and annotations  
3. Use [🔪 Slices](spb_onprem/slices/README.md) - Organize data into logical groups

#### **🚀 ML Pipeline Integration**
1. Begin with [📊 Data](spb_onprem/data/README.md) - Understand data structure and filtering
2. Configure [⚡ Activities](spb_onprem/activities/README.md) - Automate labeling and review workflows
3. Setup [📤 Exports](spb_onprem/exports/README.md) - Export to ML training formats
4. Track with [🤖 Models](spb_onprem/models/README.md) - Register and monitor model performance
5. Visualize with [📈 Reports](spb_onprem/reports/README.md) - Generate analytics dashboardss.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/pypi/v/superb-ai-onprem.svg)

**Superb AI On-premise Python SDK** is a comprehensive Python library that provides a simple and intuitive interface to interact with your on-premise Superb AI installation. Build powerful data management, annotation, and machine learning workflows with ease.

## 🌟 Key Features

- **🗂️ Dataset Management**: Create, organize, and manage your datasets
- **📊 Data Operations**: Upload, annotate, and manipulate your data with powerful filtering
- **🔍 Advanced Filtering**: Sophisticated filtering system for precise data queries  
- **🏷️ Annotation Management**: Handle annotations and versions seamlessly
- **📤 Export & Import**: Flexible data export and content management
- **⚡ Activity Tracking**: Monitor and manage long-running tasks
- **🔧 Slice Management**: Organize data into logical groups

## 🔧 Installation

### Step 1: Install the SDK

Install the SDK using pip:

```bash
pip install superb-ai-onprem
```

**Requirements:**
- Python 3.7 or higher
- Active Superb AI On-premise installation

> ⚠️ **Important**: The SDK will not work without this configuration file. Make sure to replace the values with your actual credentials from your Superb AI administrator.

## 🚀 Quick Start

Get up and running with Superb AI SDK in minutes:

### Step 1: Authentication Setup

First, set up your authentication credentials:

**Option A: Config file (Recommended for local development)**
```bash
# Create config directory
mkdir -p ~/.spb

# Create config file
cat > ~/.spb/onprem-config << EOF
[default]
host=https://your-superb-ai-host.com
access_key=your-access-key
access_key_secret=your-access-key-secret
EOF
```

### Step 2: Your First Workflow

```python
from spb_onprem import DatasetService, DataService, ModelService, ReportService

# Initialize services
dataset_service = DatasetService()
data_service = DataService()
model_service = ModelService()
report_service = ReportService()

# 1. Find existing datasets
datasets, cursor, total = dataset_service.get_datasets(length=10)
print(f"📂 Found {total} datasets")

if datasets:
    # Use the first available dataset
    dataset = datasets[0]
    print(f"✅ Using dataset: {dataset.name} (ID: {dataset.id})")
    
    # 2. Get data list from the dataset
    data_list, cursor, total = data_service.get_data_list(
        dataset_id=dataset.id,
        length=10
    )
    
    print(f"📊 Dataset contains {total} data items")
    
    # 3. Display data information
    for i, data in enumerate(data_list, 1):
        print(f"  {i}. Key: {data.key}, Type: {data.type}, ID: {data.id}")
        
    if total > len(data_list):
        print(f"  ... and {total - len(data_list)} more items")
    
    # 4. Check models in the dataset
    models, _, model_count = model_service.get_models(
        dataset_id=dataset.id,
        length=5
    )
    
    if model_count > 0:
        print(f"\n🤖 Found {model_count} models")
        for model in models:
            print(f"  - {model.name} ({model.baseline_model})")
    
    # 5. Check analytics reports
    reports, _, report_count = report_service.get_analytics_reports(
        dataset_id=dataset.id,
        length=5
    )
    
    if report_count > 0:
        print(f"\n📈 Found {report_count} analytics reports")
        for report in reports:
            print(f"  - {report.title}")
else:
    print("❌ No datasets found. Please create a dataset first.")
```

**🎉 Congratulations!** You've successfully:
- ✅ Connected to your Superb AI instance
- ✅ Found existing datasets
- ✅ Retrieved and displayed data information
- ✅ Explored models and reports

Ready for more? Check out our [comprehensive documentation](#-documentation) below!

## 📚 Module Documentation

### 🏗️ Core Modules

Comprehensive guides for each SDK module with detailed examples and best practices:

| Module | Purpose | Key Features | Documentation |
|--------|---------|--------------|---------------|
| **📁 Datasets** | Dataset lifecycle management | Create, organize, manage data collections | [📂 Dataset Guide](spb_onprem/datasets/README.md) |
| **📊 Data** | Individual data management | CRUD operations, advanced filtering, annotations | [📊 Data Guide](spb_onprem/data/README.md) |
| **🔪 Slices** | Data organization & filtering | Create filtered views, team collaboration | [🔪 Slice Guide](spb_onprem/slices/README.md) |
| **⚡ Activities** | Workflow & task management | Process automation, progress tracking | [⚡ Activity Guide](spb_onprem/activities/README.md) |
| **📤 Exports** | Data & annotation export | Multi-format export (COCO, YOLO, Custom) | [📤 Export Guide](spb_onprem/exports/README.md) |
| **🤖 Models** | ML model management | Track models, training configs, performance metrics | [🤖 Model Guide](spb_onprem/models/README.md) |
| **📈 Reports** | Analytics & visualization | Create reports, charts, dashboards | [📈 Report Guide](spb_onprem/reports/README.md) |

### 🎯 Getting Started Paths

Choose your learning path based on your use case:

#### **📊 Data Management Workflow**
1. Start with [� Datasets](spb_onprem/datasets/README.md) - Create and organize your data collections
2. Then explore [📊 Data](spb_onprem/data/README.md) - Manage individual items and annotations  
3. Use [🔪 Slices](spb_onprem/slices/README.md) - Organize data into logical groups

#### **🚀 ML Pipeline Integration**
1. Begin with [� Data](spb_onprem/data/README.md) - Understand data structure and filtering
2. Configure [⚡ Activities](spb_onprem/activities/README.md) - Automate labeling and review workflows
3. Setup [� Exports](spb_onprem/exports/README.md) - Export to ML training formats

#### **👥 Team Collaboration**
1. Setup [📁 Datasets](spb_onprem/datasets/README.md) - Organize team projects  
2. Create [🔪 Slices](spb_onprem/slices/README.md) - Assign work to team members
3. Implement [⚡ Activities](spb_onprem/activities/README.md) - Track progress and quality

### 🔧 Advanced Features

Each module includes:
- **🎯 Quick Start Examples** - Get running immediately
- **📋 Detailed Entity Documentation** - Pydantic models with comprehensive field descriptions  
- **🔍 Advanced Usage Patterns** - Best practices and complex workflows
- **🔗 Cross-Module Integration** - How modules work together
- **⚡ Performance Tips** - Optimization recommendations

### 🌐 Module Relationships

```
📁 Datasets (containers)
├── 📊 Data (individual items) 
│   ├── 🔪 Slices (filtered views)
│   │   └── 🤖 Models (training configs)
│   └── ⚡ Activities (processing workflows)
├── 📤 Exports (output formats)
└── 📈 Reports (analytics & visualizations)
```

### 🆕 New Modules (v2.0+)

| Module | Added | Status | Description |
|--------|-------|--------|-------------|
| **🤖 Models** | v2.0 | ✅ Stable | ML model lifecycle management and performance tracking |
| **📈 Reports** | v2.0 | ✅ Stable | Analytics reports and visualization dashboards |

### ⚠️ Deprecated Modules

| Module | Status | Migration Path |
|--------|--------|----------------|
| **InferService** | 🚫 Deprecated | Use [🤖 Models](spb_onprem/models/README.md) for model management and [⚡ Activities](spb_onprem/activities/README.md) for inference workflows |





## ⚠️ Error Handling

The SDK provides specific error types for different scenarios:

```python
from spb_onprem.exceptions import (
    BadParameterError,
    NotFoundError,
    UnknownError
)

try:
    dataset = dataset_service.get_dataset(dataset_id="non-existent-id")
except NotFoundError:
    print("Dataset not found")
except BadParameterError as e:
    print(f"Invalid parameter: {e}")
except UnknownError as e:
    print(f"An unexpected error occurred: {e}")
```


## 🧪 Requirements

- Python >= 3.7
- requests >= 2.22.0
- urllib3 >= 1.21.1
- pydantic >= 1.8.0

## 🤝 Contributing

We welcome contributions to the Superb AI On-premise SDK! Here's how you can help:

### Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Superb-AI-Suite/superb-ai-onprem-python.git
cd superb-ai-onprem-python
```

2. **Install development dependencies:**
```bash
pip install -e ".[dev]"
```

### Contribution Guidelines

- **Code Style:** Follow PEP 8 guidelines
- **Testing:** Add tests for new features
- **Documentation:** Update docstrings and README
- **Pull Requests:** Use descriptive titles and include test results

### Reporting Issues

When reporting issues, please include:
- SDK version (`spb_onprem.__version__`)
- Python version
- Error messages and stack traces
- Minimal reproduction example
- Expected vs actual behavior

## 📞 Support

### Community Support
- **GitHub Issues:** [Report bugs and request features](https://github.com/Superb-AI-Suite/superb-ai-onprem-python/issues)
- **Documentation:** [Official API documentation](https://docs.superb-ai.com)

### Enterprise Support
- **Technical Support:** Contact your Superb AI representative
- **Custom Integration:** Professional services available
- **Training:** SDK workshops and onboarding sessions

### Quick Help

**Common Issues:**
- **Authentication errors:** Check config file format and credentials
- **Connection issues:** Verify host URL and network connectivity  
- **Import errors:** Ensure SDK is properly installed (`pip install superb-ai-onprem`)
- **Performance issues:** Use appropriate pagination and filtering

**Need immediate help?** Check our [FAQ section](https://docs.superb-ai.com/faq) or contact support.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🚀 Ready to build something amazing?** Start with our [Quick Start Guide](#-quick-start) and explore the powerful features of Superb AI On-premise SDK!

<div align="center">
  <sub>Built with ❤️ by the <a href="https://superb-ai.com">Superb AI</a> team</sub>
</div>

