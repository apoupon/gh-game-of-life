# gh-game-of-life

Transform your GitHub contribution graph into Conway's Game of Life.

![Example](example.gif)

## Usage

### One time generation

Check out the [web demo](https://gh-game-of-life-vercel-deployment.vercel.app/) and generate a GIF in seconds without installing anything locally.

### GitHub Action

Automatically update your game GIF daily using GitHub Actions! Add this workflow to your repository at `.github/workflows/update-game.yml`:
```yaml
name: Update Game of Life Game

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:  # Allow manual trigger

permissions:
  contents: write

jobs:
  update-game:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: apoupon/gh-game-of-life@v1.1.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          output-path: 'game.gif'
          strategy: 'loop'
```

Then display it in your README:
```markdown
![My GitHub Game](game.gif)
```

### From PyPI

```bash
pip install gh-game-of-life
```

### From source

```bash
# Clone the repository
git clone https://github.com/apoupon/gh-game-of-life.git
cd gh-game-of-life

# Install with uv
uv sync

# Or with pip
pip install -e .
```

## Setup

1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `read:user`
   - Copy the generated token

2. Set up your environment:
   ```bash
   # Copy the example env file
   touch .env
   echo "GITHUB_TOKEN=your_token_here" >> .env
   ```

   Alternatively, export the token directly:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

## Usage

### Generate Your Game GIF

```bash
# Basic usage - generates username-gh-life.gif
gh-game-of-life <username>

# Specify output filename
gh-game-of-life torvalds --output my-gif.gif
gh-game-of-life torvalds -o torvalds-life.gif

# Adjust the number of simulation frames
gh-game-of-life torvalds --frames 100
gh-game-of-life torvalds -f 200

# Control frame delay (milliseconds per frame)
gh-game-of-life torvalds --frame-delay 500
gh-game-of-life torvalds -d 250

# Load settings from a YAML configuration file
gh-game-of-life --config config.yaml
```

### Create cool patterns

You can design and test your own patterns using the `have_fun` notebook. The third cell contains an interactive canvas where you can "paint" on the grid and watch it evolve.

## On Conway's Game of Life

The Game of Life is a cellular automaton devised by the British mathematician John Horton Conway in 1970. It is a zero-player game meaning that its evolution is determined by its initial state, requiring no further input. Despite being governed by just three simple rules, it can give rise to incredibly complex behaviors and patterns. The Game of Life is a perfect example of how simple rules can generate unexpected complexity.

A cool documentary on Conway's Game of Life can be found here: https://www.youtube.com/watch?v=Kk2MH9O4pXY

## On the Quad Life variant

An interesting variation of the Life rules is to use several distinct living state, with each behaving according to Life rules, but, in addition, carrying independent color information. The color of each newly-born bit is determined by the color of its parents. Resulting patterns have exactly the same life/death behavior as in normal Life, but the colors of resulting bits provides interesting additional complexity.

This project uses the Quad-Life variant, which employs four symmetrical colors, creating vibrant, evolving patterns while maintaining the familiar Life behavior.

## Coding with AI

This project also serves as an experiment in coding with AI assistants. I have been using LLMs in my development workflow for a while but had not yet explored specialized coding agents such as Claude Code, Cursor, or GitHub Copilot in Agent mode. For this project, I experimented with GitHub Copilot and Claude Sonnet 4.5, taking the project from initial idea to working implementation.

I drew inspiration from the [BMAD method](https://docs.bmad-method.org/) and followed a structured workflow: starting with a product brief, then moving through product requirement design, UX design, software architecture, and breaking work into epics and stories. Development and testing occurred in iterative loops, completing tests before moving on to the next story or epic.

It was smooth and fast.

## Acknowledgements

I got the idea from [czl9707's Github Space Shooter](https://github.com/czl9707/gh-space-shooter) and discovered the Quad Life variant of the Conway's game of life through [this resource](https://conwaylife.com/ref/mniemiec/color.htm#c-imm).
