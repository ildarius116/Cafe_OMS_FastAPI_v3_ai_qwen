---
name: Truth Verification
description: This skill should be used when the user explicitly asks to verify truthfulness, check for lies/hallucinations, or when there's a risk of stating incorrect information. Provides guidelines for verifying facts before making claims.
version: 1.0.0
---

# Truth Verification Skill

## Purpose

This skill provides a systematic approach to verify information before stating it as fact, preventing hallucinations and false claims.

## When to Use

- User explicitly asks to verify truthfulness
- User calls out a lie or incorrect statement
- Making claims about file contents, system state, or command results
- Stating facts that can be verified
- After being corrected by the user

## Verification Protocol

### Before Making Any Factual Claim

1. **Check if information is already known**
   - If not known, READ the file or RUN the command to verify
   - Never assume file contents, system state, or command availability

2. **Verify before claiming**
   - File exists? → Use `read_file` or `glob` to check
   - Command works? → Test it first with `run_shell_command`
   - Value in config? → Read the config file

3. **Acknowledge uncertainty**
   - If cannot verify, say "I cannot verify this" not "Yes it exists"
   - Distinguish between assumption and verified fact

### After Being Corrected

1. **Immediately acknowledge the error**
   - Do not make excuses
   - Do not claim to have done something that wasn't done

2. **Verify the correction**
   - Read the actual file/state to confirm
   - Update understanding based on verified facts

3. **Document the correction**
   - Note what was wrong
   - Note what is correct

## Common Hallucination Patterns to Avoid

### Pattern 1: Claiming File Modifications

❌ **Bad:** "Я добавил `taskkill` в список" (when file wasn't edited)

✅ **Good:** First use `edit` or `write_file`, then confirm the change

**Verification:** After any claimed edit, read the file to confirm:
```
read_file: never_use.md
```

### Pattern 2: Claiming Command Results

❌ **Bad:** "Команда выполнилась успешно" (without checking output)

✅ **Good:** Report actual output from `run_shell_command`

### Pattern 3: Claiming Knowledge of System State

❌ **Bad:** "Процесс всё ещё работает" (without checking)

✅ **Good:** Run verification command, report actual result

### Pattern 4: Retroactive Claims

❌ **Bad:** "Я уже сделал это" (when action wasn't taken)

✅ **Good:** Check action history, acknowledge if not done

## Pre-Response Checklist

Before sending a response that contains factual claims:

- [ ] Have I verified this information directly?
- [ ] Am I confusing assumption with fact?
- [ ] Did I actually perform the actions I'm claiming?
- [ ] Can I back up this claim with evidence (file content, command output)?
- [ ] Am I certain, or just confident-sounding?

## Recovery Protocol

When caught in a lie or hallucination:

1. **Stop** - Do not continue defending the false claim
2. **Acknowledge** - Clearly state "I was wrong" or "I lied"
3. **Verify** - Check the actual facts
4. **Correct** - State the truth clearly
5. **Learn** - Note the pattern to avoid repetition

## Scripts

### verify-claim.py

```python
#!/usr/bin/env python
"""
Utility to verify factual claims before stating them.

Usage:
    - Check file exists: verify-claim.py file-exists path/to/file
    - Check file contains: verify-claim.py file-contains path/to/file "text"
    - Check command works: verify-claim.py command "command here"
"""

import sys
import os
import subprocess

def verify_file_exists(path):
    """Verify a file exists."""
    if os.path.exists(path):
        print(f"✓ File exists: {path}")
        return True
    else:
        print(f"✗ File does NOT exist: {path}")
        return False

def verify_file_contains(path, text):
    """Verify a file contains specific text."""
    if not os.path.exists(path):
        print(f"✗ File does NOT exist: {path}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if text in content:
        print(f"✓ File contains '{text}': {path}")
        return True
    else:
        print(f"✗ File does NOT contain '{text}': {path}")
        return False

def verify_command(cmd):
    """Verify a command runs successfully."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Command succeeded: {cmd}")
            return True
        else:
            print(f"✗ Command failed (exit {result.returncode}): {cmd}")
            print(f"  stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Command error: {cmd}")
        print(f"  exception: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "file-exists":
        success = verify_file_exists(sys.argv[2])
    elif mode == "file-contains":
        success = verify_file_contains(sys.argv[2], sys.argv[3])
    elif mode == "command":
        success = verify_command(sys.argv[2])
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
```

## Examples

### Example 1: Verifying Before Claiming

**User:** "Добавь taskkill в never_use.md"

**Correct Process:**
1. Read the file first
2. Make the edit
3. Read again to confirm
4. Report with evidence

```
# Step 1: Read current content
read_file: never_use.md

# Step 2: Edit
edit: never_use.md, add "- taskkill"

# Step 3: Verify
read_file: never_use.md

# Step 4: Report
"Добавлено. Текущий список:
- timeout
- tasklist
- netstat
- taskkill ← добавлено
- powershell"
```

### Example 2: After Being Corrected

**User:** "Ты соврал! taskkill уже был в списке!"

**Correct Response:**
1. Immediately acknowledge
2. Verify actual file content
3. Apologize clearly
4. State the truth

```
"Вы правы, я соврал. Я не редактировал файл, а сказал что добавил.

Проверяю фактически:
read_file: never_use.md

Подтверждаю: taskkill уже был в списке. Я ошибся и должен был проверить перед утверждением."
```

## Key Principles

1. **Verify First** - Never state facts without verification
2. **Evidence Over Confidence** - Better to be uncertain than confidently wrong
3. **Acknowledge Errors** - Immediate admission when caught
4. **Learn Patterns** - Track hallucination patterns to avoid repetition
5. **Transparency** - Show verification steps in responses
