#!/bin/bash
# VoxaCommunications Registry Run Script

# Settings variables
APP_DIR="$(dirname "$(realpath "$0")")"
SRC_DIR="$APP_DIR/src"
LOG_DIR="$APP_DIR/logs"
TOOL_LOG_DIR="$LOG_DIR/tools"
LINT_OUTPUT="$TOOL_LOG_DIR/flake8_output.log"
TYPE_CHECK_OUTPUT="$TOOL_LOG_DIR/mypy_output.log"
PYTHON_CMD="python"
DEBUG_MODE=${DEBUG_MODE:-true}
SKIP_CHECKS=${SKIP_CHECKS:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$LOG_DIR"
mkdir -p "$TOOL_LOG_DIR"

echo -e "${GREEN}Starting Registry${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
$PYTHON_CMD -m pip install -r requirements.txt

# Run linting with flake8
if [ "$SKIP_CHECKS" = false ]; then
    echo -e "${YELLOW}Running code linting with flake8...${NC}"
    $PYTHON_CMD -m flake8 "$SRC_DIR" --output-file="$LINT_OUTPUT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Linting passed successfully.${NC}"
    else
        echo -e "${RED}Linting found issues. Check $LINT_OUTPUT for details.${NC}"
        if [ "$DEBUG_MODE" = false ]; then
            echo -e "${YELLOW}Continuing despite linting issues...${NC}"
        fi
    fi
    
    # Run type checking with mypy
    echo -e "${YELLOW}Running type checking with mypy...${NC}"
    $PYTHON_CMD -m mypy "$SRC_DIR" --config-file="$APP_DIR/mypy.ini" > "$TYPE_CHECK_OUTPUT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Type checking passed successfully.${NC}"
    else
        echo -e "${RED}Type checking found issues. Check $TYPE_CHECK_OUTPUT for details.${NC}"
        if [ "$DEBUG_MODE" = false ]; then
            echo -e "${YELLOW}Continuing despite type checking issues...${NC}"
        fi
    fi
else
    echo -e "${YELLOW}Skipping linting and type checking.${NC}"
fi

# Run the application
echo -e "${GREEN}Starting application...${NC}"
$PYTHON_CMD "$SRC_DIR/main.py"