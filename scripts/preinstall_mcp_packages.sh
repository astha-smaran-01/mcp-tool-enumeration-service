#!/bin/bash

# Pre-install popular MCP packages for npx and uvx
# This script is designed to be run during Docker build time

set -e

echo "🚀 Starting MCP package pre-installation..."

# Function to install npx packages
install_npx_packages() {
    echo "📦 Installing popular npx MCP packages..."
    
    # Core MCP packages (most likely to exist)
    local core_packages=(
        "@mcp-remote"
        # "@modelcontextprotocol/server-everything"
        # "@modelcontextprotocol/server-filesystem"
        # "@modelcontextprotocol/server-git"
        # "@modelcontextprotocol/server-memory"
        # "@modelcontextprotocol/server-postgres"
        # "@modelcontextprotocol/server-sqlite"
        # "@modelcontextprotocol/server-brave-search"
        # "@modelcontextprotocol/server-github"
    )
    
    # Popular third-party packages
    local popular_packages=(
        "@paypal/mcp"
        # "@stripe/mcp"
        # "@shopify/mcp"
        # "@salesforce/mcp"
        # "@hubspot/mcp"
        # "@zendesk/mcp"
        # "@intercom/mcp"
        # "@slack/mcp"
        # "@discord/mcp"
        # "@github/mcp"
        # "@gitlab/mcp"
        # "@bitbucket/mcp"
        # "@jira/mcp"
        # "@confluence/mcp"
        # "@notion/mcp"
        # "@airtable/mcp"
        # "@trello/mcp"
        # "@asana/mcp"
        # "@monday/mcp"
        # "@clickup/mcp"
        # "@linear/mcp"
        # "@figma/mcp"
        # "@sketch/mcp"
        # "@adobe/mcp"
        # "@canva/mcp"
        # "@unsplash/mcp"
        # "@pexels/mcp"
        # "@shutterstock/mcp"
        # "@square/mcp"
        # "@woocommerce/mcp"
        # "@magento/mcp"
        # "@bigcommerce/mcp"
        # "@pipedrive/mcp"
        # "@freshdesk/mcp"
        # "@drift/mcp"
        # "@crisp/mcp"
        # "@tawk/mcp"
        # "@livechat/mcp"
        # "@helpscout/mcp"
        # "@kayako/mcp"
        # "@uservoice/mcp"
        # "@feedback/mcp"
        # "@survey/mcp"
        # "@typeform/mcp"
        # "@surveymonkey/mcp"
        # "@google-forms/mcp"
        # "@calendly/mcp"
        # "@acuity/mcp"
        # "@calendso/mcp"
        # "@when2meet/mcp"
        # "@doodle/mcp"
        # "@zoom/mcp"
        # "@teams/mcp"
        # "@meet/mcp"
        # "@webex/mcp"
        # "@gotomeeting/mcp"
        # "@skype/mcp"
        # "@whatsapp/mcp"
        # "@telegram/mcp"
        # "@signal/mcp"
        # "@viber/mcp"
        # "@line/mcp"
        # "@wechat/mcp"
        # "@qq/mcp"
        # "@kakaotalk/mcp"
        # "@snapchat/mcp"
        # "@instagram/mcp"
        # "@facebook/mcp"
        # "@linkedin/mcp"
        # "@tiktok/mcp"
        # "@pinterest/mcp"
        # "@tumblr/mcp"
        # "@medium/mcp"
        # "@dev/mcp"
        # "@hashnode/mcp"
        # "@ghost/mcp"
        # "@wordpress/mcp"
        # "@squarespace/mcp"
        # "@wix/mcp"
        # "@webflow/mcp"
        # "@framer/mcp"
        # "@bubble/mcp"
        # "@adalo/mcp"
        # "@glide/mcp"
        # "@zapier/mcp"
        # "@ifttt/mcp"
        # "@make/mcp"
        # "@automate/mcp"
        # "@integromat/mcp"
        # "@pipedream/mcp"
        # "@n8n/mcp"
        # "@huggingface/mcp"
        # "@openai/mcp"
        # "@anthropic/mcp"
        # "@cohere/mcp"
        # "@replicate/mcp"
        # "@runpod/mcp"
        # "@lambda/mcp"
        # "@vertex/mcp"
        # "@bedrock/mcp"
        # "@watson/mcp"
        # "@azure-cognitive/mcp"
        # "@clarifai/mcp"
        # "@imagga/mcp"
        # "@cloudinary/mcp"
        # "@imgix/mcp"
        # "@uploadcare/mcp"
        # "@filestack/mcp"
        # "@transloadit/mcp"
        # "@bannerbear/mcp"
        # "@remove-bg/mcp"
        # "@photoshop/mcp"
        # "@gimp/mcp"
        # "@invision/mcp"
        # "@marvel/mcp"
        # "@principle/mcp"
        # "@origami/mcp"
        # "@flinto/mcp"
        # "@protopie/mcp"
        # "@axure/mcp"
        # "@balsamiq/mcp"
        # "@mockflow/mcp"
        # "@wireframe/mcp"
        # "@draw/mcp"
        # "@lucidchart/mcp"
        # "@visio/mcp"
        # "@omnigraffle/mcp"
        # "@cacoo/mcp"
        # "@gliffy/mcp"
        # "@creately/mcp"
        # "@smartdraw/mcp"
        # "@edraw/mcp"
        # "@yed/mcp"
        # "@graphviz/mcp"
        # "@plantuml/mcp"
        # "@mermaid/mcp"
        # "@drawio/mcp"
        # "@excalidraw/mcp"
        # "@tldraw/mcp"
    )
    
    # Install core packages first
    for package in "${core_packages[@]}"; do
        echo "Installing $package..."
        if npx -y "$package" --version > /dev/null 2>&1; then
            echo "✅ $package installed successfully"
        else
            echo "⚠️  $package not available or failed to install"
        fi
    done
    
    # Install popular packages
    for package in "${popular_packages[@]}"; do
        echo "Installing $package..."
        if npx -y "$package" --version > /dev/null 2>&1; then
            echo "✅ $package installed successfully"
        else
            echo "⚠️  $package not available or failed to install"
        fi
    done
    
    echo "📦 npx package installation completed"
}

# Function to install uvx packages
install_uvx_packages() {
    echo "🐍 Installing popular uvx MCP packages..."
    
    # Check if uvx is available
    if ! command -v uvx &> /dev/null; then
        echo "⚠️  uvx not available, skipping uvx package installation"
        return
    fi
    
    # Core MCP packages for uvx
    local core_packages=(
        "mcp-proxy"
        # "github-chat-mcp"
        # "mcp-server-filesystem"
        # "mcp-server-git"
        # "mcp-server-memory"
        # "mcp-server-postgres"
        # "mcp-server-sqlite"
        # "mcp-server-brave-search"
        # "mcp-server-github"
    )
    
    # Popular third-party packages for uvx
    local popular_packages=(
        # "mcp-server-slack"
        # "mcp-server-discord"
        # "mcp-server-twitter"
        # "mcp-server-reddit"
        # "mcp-server-youtube"
        # "mcp-server-weather"
        # "mcp-server-news"
        # "mcp-server-wikipedia"
        # "mcp-server-stackoverflow"
        # "mcp-server-aws"
        # "mcp-server-gcp"
        # "mcp-server-azure"
        # "mcp-server-docker"
        # "mcp-server-kubernetes"
        # "mcp-server-terraform"
        # "mcp-server-ansible"
        # "mcp-server-puppet"
        # "mcp-server-chef"
        # "mcp-server-jenkins"
        # "mcp-server-gitlab"
        # "mcp-server-bitbucket"
        # "mcp-server-jira"
        # "mcp-server-confluence"
        # "mcp-server-notion"
        # "mcp-server-airtable"
        # "mcp-server-trello"
        # "mcp-server-asana"
        # "mcp-server-monday"
        # "mcp-server-clickup"
        # "mcp-server-linear"
        # "mcp-server-figma"
        # "mcp-server-sketch"
        # "mcp-server-adobe"
        # "mcp-server-canva"
        # "mcp-server-unsplash"
        # "mcp-server-pexels"
        # "mcp-server-shutterstock"
        # "mcp-server-stripe"
        # "mcp-server-paypal"
        # "mcp-server-square"
        # "mcp-server-shopify"
        # "mcp-server-woocommerce"
        # "mcp-server-magento"
        # "mcp-server-bigcommerce"
        # "mcp-server-salesforce"
        # "mcp-server-hubspot"
        # "mcp-server-pipedrive"
        # "mcp-server-zendesk"
        # "mcp-server-freshdesk"
        # "mcp-server-intercom"
        # "mcp-server-drift"
        # "mcp-server-crisp"
        # "mcp-server-tawk"
        # "mcp-server-livechat"
        # "mcp-server-helpscout"
        # "mcp-server-kayako"
        # "mcp-server-uservoice"
        # "mcp-server-feedback"
        # "mcp-server-survey"
        # "mcp-server-typeform"
        # "mcp-server-surveymonkey"
        # "mcp-server-google-forms"
        # "mcp-server-calendly"
        # "mcp-server-acuity"
        # "mcp-server-calendso"
        # "mcp-server-when2meet"
        # "mcp-server-doodle"
        # "mcp-server-zoom"
        # "mcp-server-teams"
        # "mcp-server-meet"
        # "mcp-server-webex"
        # "mcp-server-gotomeeting"
        # "mcp-server-skype"
        # "mcp-server-whatsapp"
        # "mcp-server-telegram"
        # "mcp-server-signal"
        # "mcp-server-viber"
        # "mcp-server-line"
        # "mcp-server-wechat"
        # "mcp-server-qq"
        # "mcp-server-kakaotalk"
        # "mcp-server-snapchat"
        # "mcp-server-instagram"
        # "mcp-server-facebook"
        # "mcp-server-linkedin"
        # "mcp-server-tiktok"
        # "mcp-server-pinterest"
        # "mcp-server-tumblr"
        # "mcp-server-medium"
        # "mcp-server-dev"
        # "mcp-server-hashnode"
        # "mcp-server-ghost"
        # "mcp-server-wordpress"
        # "mcp-server-squarespace"
        # "mcp-server-wix"
        # "mcp-server-webflow"
        # "mcp-server-framer"
        # "mcp-server-bubble"
        # "mcp-server-adalo"
        # "mcp-server-glide"
        # "mcp-server-zapier"
        # "mcp-server-ifttt"
        # "mcp-server-make"
        # "mcp-server-automate"
        # "mcp-server-integromat"
        # "mcp-server-pipedream"
        # "mcp-server-n8n"
        # "mcp-server-huggingface"
        # "mcp-server-openai"
        # "mcp-server-anthropic"
        # "mcp-server-cohere"
        # "mcp-server-replicate"
        # "mcp-server-runpod"
        # "mcp-server-lambda"
        # "mcp-server-vertex"
        # "mcp-server-bedrock"
        # "mcp-server-watson"
        # "mcp-server-azure-cognitive"
        # "mcp-server-clarifai"
        # "mcp-server-imagga"
        # "mcp-server-cloudinary"
        # "mcp-server-imgix"
        # "mcp-server-uploadcare"
        # "mcp-server-filestack"
        # "mcp-server-transloadit"
        # "mcp-server-bannerbear"
        # "mcp-server-remove-bg"
        # "mcp-server-photoshop"
        # "mcp-server-gimp"
        # "mcp-server-invision"
        # "mcp-server-marvel"
        # "mcp-server-principle"
        # "mcp-server-origami"
        # "mcp-server-flinto"
        # "mcp-server-protopie"
        # "mcp-server-axure"
        # "mcp-server-balsamiq"
        # "mcp-server-mockflow"
        # "mcp-server-wireframe"
        # "mcp-server-draw"
        # "mcp-server-lucidchart"
        # "mcp-server-visio"
        # "mcp-server-omnigraffle"
        # "mcp-server-cacoo"
        # "mcp-server-gliffy"
        # "mcp-server-creately"
        # "mcp-server-smartdraw"
        # "mcp-server-edraw"
        # "mcp-server-yed"
        # "mcp-server-graphviz"
        # "mcp-server-plantuml"
        # "mcp-server-mermaid"
        # "mcp-server-drawio"
        # "mcp-server-excalidraw"
        # "mcp-server-tldraw"
    )
    
    # Install core packages first
    for package in "${core_packages[@]}"; do
        echo "Installing $package..."
        if uvx "$package" --help > /dev/null 2>&1; then
            echo "✅ $package installed successfully"
        else
            echo "⚠️  $package not available or failed to install"
        fi
    done
    
    # Install popular packages
    for package in "${popular_packages[@]}"; do
        echo "Installing $package..."
        if uvx "$package" --help > /dev/null 2>&1; then
            echo "✅ $package installed successfully"
        else
            echo "⚠️  $package not available or failed to install"
        fi
    done
    
    echo "🐍 uvx package installation completed"
}

# Main execution
main() {
    echo "🔧 Checking prerequisites..."
    
    # Check if npx is available
    if command -v npx &> /dev/null; then
        echo "✅ npx is available"
        install_npx_packages
    else
        echo "❌ npx not available, skipping npx package installation"
    fi
    
    # Check if uvx is available
    if command -v uvx &> /dev/null; then
        echo "✅ uvx is available"
        install_uvx_packages
    else
        echo "❌ uvx not available, skipping uvx package installation"
    fi
    
    echo "🎉 MCP package pre-installation completed!"
}

# Run main function
main "$@"