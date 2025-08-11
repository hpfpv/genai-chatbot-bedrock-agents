# 🤖 GenAI Chatbot with Bedrock Agents

**Exploring the Evolution of AI-Infrastructure Integration**

This repository demonstrates two distinct approaches to building AI-powered AWS infrastructure management tools, showcasing the technical evolution from custom tool development to standardized protocols.

## 🎯 **Purpose**

Originally created to demonstrate the potential of generative AI in business processes, this project has evolved into an educational comparison between traditional custom tool development and modern protocol-based approaches. It provides insights into architectural decisions, development complexity, and the benefits of community-maintained integrations.

## 📁 **Project Structure**

### **[`no-mcp-chatbot/`](./no-mcp-chatbot/)** - Traditional Custom Tools Approach
- **Technology**: LangChain + Custom Python Functions + Amazon Bedrock
- **Architecture**: User → Streamlit → LangChain Agent → Custom Tools → AWS APIs
- **Development**: Manual tool creation for each AWS service
- **Maintenance**: Custom error handling and API updates required
- **Scope**: Limited to explicitly implemented services

**Key Features:**
- 🛠️ Hand-built AWS tools (EC2, S3 operations)
- 🧠 LangChain agent orchestration
- 🔍 Optional web search integration

### **[`mcp-chatbot/`](./mcp-chatbot/)** - Modern MCP Protocol Approach
- **Technology**: Model Context Protocol + Official AWS Labs MCP Servers + Amazon Bedrock
- **Architecture**: User → Enhanced Streamlit → Simple Agent → MCP Client → AWS MCP Servers
- **Development**: Leverages standardized, community-maintained servers
- **Maintenance**: Automatic updates through official AWS integrations
- **Scope**: Full AWS CLI access + comprehensive documentation

**Key Features:**
- 🔌 Official AWS Labs MCP servers integration
- 🔐 AWS SSO authentication
- 📚 Built-in AWS documentation access
- 🔍 Real-time debug monitoring

---

**🔗 Related Resources:**
- [AWS Labs MCP Servers](https://github.com/awslabs/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain Framework](https://python.langchain.com/)
