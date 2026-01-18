"""FastAPI Demo API for Game of Life GIF Generator.

Provides stateless, timeout-protected endpoint to generate GIFs from GitHub usernames.
"""

import asyncio
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from gh_game_of_life.core.game import BoundaryStrategy
from gh_game_of_life.generate import generate_gif

# Configuration
DEFAULT_FRAMES = 20
DEFAULT_STRATEGY = "void"
MAX_FRAMES = 100
TIMEOUT_SECONDS = 60  # 60 second timeout for Vercel free tier

# Initialize FastAPI app
app = FastAPI(
    title="Game of Life GIF Generator",
    description="Transform GitHub contribution graphs into Conway's Game of Life animations",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/generate")
async def generate_gif_endpoint(
    username: str = Query(..., description="GitHub username to generate GIF from"),
    frames: int = Query(
        DEFAULT_FRAMES,
        ge=1,
        le=MAX_FRAMES,
        description="Number of simulation frames (1-100)",
    ),
    strategy: str = Query(
        DEFAULT_STRATEGY,
        description="Boundary strategy: 'void' or 'loop'",
    ),
) -> StreamingResponse:
    """Generate a Game of Life GIF from GitHub contribution data.

    Query Parameters:
    - username (required): GitHub username
    - frames: Number of frames (default: 20, max: 100)
    - strategy: 'void' (default) or 'loop'

    Returns:
    - Streaming GIF file with appropriate MIME type
    """
    # Validate inputs
    if not username or len(username) == 0:
        raise HTTPException(status_code=400, detail="username is required")

    if len(username) > 255:
        raise HTTPException(status_code=400, detail="username too long")

    if strategy not in ["void", "loop"]:
        raise HTTPException(
            status_code=400,
            detail="strategy must be 'void' or 'loop'",
        )

    try:
        # Create temporary output file
        temp_file = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
        output_path = temp_file.name
        temp_file.close()

        # Convert strategy string to BoundaryStrategy enum
        boundary_strategy = (
            BoundaryStrategy.LOOP if strategy == "loop" else BoundaryStrategy.VOID
        )

        # Run generation with timeout
        gif_path = await asyncio.wait_for(
            asyncio.to_thread(
                generate_gif,
                username,
                output_path,
                frames,
                boundary_strategy,
            ),
            timeout=TIMEOUT_SECONDS,
        )

        # Read the generated GIF
        if not Path(gif_path).exists():
            raise HTTPException(
                status_code=500,
                detail="GIF generation failed: file not created",
            )

        # Open file and prepare streaming response
        file_content = Path(gif_path).read_bytes()

        # Clean up the temporary file
        try:
            Path(gif_path).unlink()
        except Exception:
            pass  # Ignore cleanup errors

        # Return as streaming response
        return StreamingResponse(
            iter([file_content]),
            media_type="image/gif",
            headers={
                "Content-Disposition": f"attachment; filename={username}-game-of-life.gif"
            },
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Generation timeout after {TIMEOUT_SECONDS} seconds. Try with fewer frames.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}",
        )


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "Game of Life GIF Generator API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "generate": "/generate?username=<github-username>&frames=20&strategy=void",
        },
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
