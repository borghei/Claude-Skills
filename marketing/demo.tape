# VHS tape — claude-skills npm CLI demo for LinkedIn post
# Run with: vhs marketing/demo.tape

Output claude-skills-demo.gif

Set FontSize 22
Set Width 1600
Set Height 900
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 50
Set Shell "bash"

Hide
Type "export NO_COLOR=1 FORCE_COLOR=0"
Enter
Type "rm -rf /tmp/claude-skills-demo && mkdir -p /tmp/claude-skills-demo/.claude && cd /tmp/claude-skills-demo && clear"
Enter
Sleep 500ms
Show

# 1. List the compliance domain (shows the wedge with real skill names)
Type "npx @borghei/claude-skills list --domain ra-qm-team"
Sleep 600ms
Enter
Sleep 5s

# 2. Install SOC 2
Type "clear"
Enter
Sleep 300ms
Type "npx @borghei/claude-skills add soc2-compliance-expert"
Sleep 600ms
Enter
Sleep 5s

# 3. Show what landed
Type "ls .claude/skills/soc2-compliance-expert/"
Sleep 400ms
Enter
Sleep 3s

# 4. Hold final frame
Sleep 2s
