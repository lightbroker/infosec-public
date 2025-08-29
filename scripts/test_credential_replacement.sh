#!/bin/bash

# Function to safely replace tokens using printf and sed
# This approach handles special characters by using printf %q for proper escaping
replace_token_safe() {
    local file="$1"
    local token="$2"
    local value="$3"
    local temp_file=$(mktemp)
    
    # Escape the replacement value for sed
    local escaped_value=$(printf '%s\n' "$value" | sed 's/[[\.*^$()+?{|]/\\&/g')
    
    # Use sed with a different delimiter to avoid issues with forward slashes
    sed "s|$token|$escaped_value|g" "$file" > "$temp_file"
    mv "$temp_file" "$file"
}

# Alternative function using awk (often more reliable with special characters)
replace_token_awk() {
    local file="$1"
    local token="$2"
    local value="$3"
    local temp_file=$(mktemp)
    
    # Use awk with gsub - handles special characters better than sed
    awk -v token="$token" -v replacement="$value" '{gsub(token, replacement); print}' "$file" > "$temp_file"
    mv "$temp_file" "$file"
}

# Most robust solution using perl (available on most systems)
replace_token_perl() {
    local file="$1"
    local token="$2"
    local value="$3"
    
    # Perl handles special characters excellently with \Q...\E literal quoting
    perl -i -pe "s/\Q$token\E/\Q$value\E/g" "$file"
}

# GitHub Actions compatible function
replace_github_secret() {
    local file="$1"
    local token="$2"
    local secret_value="$3"
    
    echo "Replacing token '$token' in file '$file'"
    
    # Choose the most robust method available
    if command -v perl >/dev/null 2>&1; then
        replace_token_perl "$file" "$token" "$secret_value"
        echo "Used perl method"
    else
        replace_token_awk "$file" "$token" "$secret_value"
        echo "Used awk method"
    fi
}

# Test function to validate replacements
run_tests() {
    echo "Running token replacement tests..."
    
    # Test passwords with various special characters
    local test_passwords=(
        "simple123"
        "pa\$\$w0rd"
        "p@ssw&rd!"
        "pass/with\\slashes"
        "reg[ex]chars"
        "dots.and*stars"
        "quotes\"and'apostrophes"
        "spaces in password"
        "$(echo 'command substitution')"
        "pipe|and&ampersand"
        "percent%signs"
        "equals=and+plus"
        "curly{braces}here"
        "parentheses(and)stuff"
        "question?marks"
        "hash#tags"
        "tilde~character"
        "backtick\`character"
    )
    
    local token="{{PASSWORD}}"
    local test_content="server:
  host: localhost
  password: $token
  connection_string: \"user:$token@localhost:5432/db\"
  config:
    secret: $token"
    
    local passed=0
    local total=0
    
    for password in "${test_passwords[@]}"; do
        ((total++))
        echo "Testing password: '$password'"
        
        # Create test file
        local test_file=$(mktemp)
        echo "$test_content" > "$test_file"
        
        # Replace token
        replace_github_secret "$test_file" "$token" "$password"
        
        # Verify replacement worked
        if grep -q "$token" "$test_file"; then
            echo "❌ FAILED: Token '$token' still found in file"
            echo "File contents:"
            cat "$test_file"
        else
            # Count occurrences of password in file
            local count=$(grep -o -F "$password" "$test_file" | wc -l)
            if [ "$count" -eq 3 ]; then
                echo "✅ PASSED: All 3 tokens replaced correctly"
                ((passed++))
            else
                echo "❌ FAILED: Expected 3 replacements, got $count"
                echo "File contents:"
                cat "$test_file"
            fi
        fi
        
        rm -f "$test_file"
        echo ""
    done
    
    echo "Test Results: $passed/$total tests passed"
    
    if [ "$passed" -eq "$total" ]; then
        echo "🎉 All tests passed!"
        return 0
    else
        echo "❌ Some tests failed!"
        return 1
    fi
}

# Example GitHub Actions usage function
github_actions_example() {
    echo "GitHub Actions Example Usage:"
    echo ""
    echo "# In your workflow file (.github/workflows/deploy.yml):"
    echo "- name: Replace secrets in config"
    echo "  run: |"
    echo "    # Source this script"
    echo "    source ./replace_tokens.sh"
    echo "    "
    echo "    # Replace tokens with secrets"
    echo "    replace_github_secret \"config/app.yml\" \"{{DB_PASSWORD}}\" \"\${{ secrets.DB_PASSWORD }}\""
    echo "    replace_github_secret \"config/app.yml\" \"{{API_KEY}}\" \"\${{ secrets.API_KEY }}\""
    echo "    replace_github_secret \"docker-compose.yml\" \"{{SECRET_TOKEN}}\" \"\${{ secrets.SECRET_TOKEN }}\""
    echo ""
    echo "# Alternative one-liner usage:"
    echo "- name: Replace password token"
    echo "  run: |"
    echo "    if command -v perl >/dev/null 2>&1; then"
    echo "      perl -i -pe 's/\Q{{PASSWORD}}\E/\Q\${{ secrets.PASSWORD }}\E/g' config.yml"
    echo "    else"
    echo "      awk -v token='{{PASSWORD}}' -v replacement='\${{ secrets.PASSWORD }}' '{gsub(token, replacement); print}' config.yml > temp && mv temp config.yml"
    echo "    fi"
}

# Main execution
case "${1:-}" in
    "test")
        run_tests
        ;;
    "example")
        github_actions_example
        ;;
    "")
        echo "Token Replacement Script"
        echo "Usage:"
        echo "  $0 test     - Run unit tests"
        echo "  $0 example  - Show GitHub Actions examples"
        echo ""
        echo "Functions available when sourced:"
        echo "  replace_github_secret <file> <token> <secret_value>"
        echo "  replace_token_safe <file> <token> <value>"
        echo "  replace_token_awk <file> <token> <value>"
        echo "  replace_token_perl <file> <token> <value>"
        ;;
    *)
        echo "Unknown command: $1"
        exit 1
        ;;
esac
