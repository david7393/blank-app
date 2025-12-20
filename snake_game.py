import streamlit as st
import streamlit.components.v1 as components

def snake_game():
    st.header("🎮 Reward Snake Game")
    st.write("Use arrow keys or on-screen buttons to control the snake. 🍎")

    # Initialize direction
    if "direction" not in st.session_state:
        st.session_state.direction = "RIGHT"

    # Embed JS Snake game
    components.html(
        f"""
        <style>
            canvas {{background-color: #000; display:block; margin:auto;}}
        </style>
        <canvas id="snakeCanvas" width="400" height="400"></canvas>
        <div id="controls" style="text-align:center; margin-top:8px;">
            <button id="btnLeft" style="font-size:20px; margin:4px;">⬅️</button>
            <button id="btnUp" style="font-size:20px; margin:4px;">⬆️</button>
            <button id="btnDown" style="font-size:20px; margin:4px;">⬇️</button>
            <button id="btnRight" style="font-size:20px; margin:4px;">➡️</button>
        </div>

        <script>
            const canvas = document.getElementById("snakeCanvas");
            const ctx = canvas.getContext("2d");
            const box = 20;
            const canvasSize = 400;

            let snake = [{{x: 9*box, y: 9*box}}];
            let food = {{x: Math.floor(Math.random()*20)*box, y: Math.floor(Math.random()*20)*box}};
            let direction = "{st.session_state.direction}";
            let score = 0;
            let countdown = 3; // seconds until game start
            let ticks = 0; // tick counter to decrement countdown every 1s (5 ticks of 200ms)
            let started = false;

            // Arrow keys for JS (optional if using Python buttons)
            document.addEventListener("keydown", function(event){{
                if(event.key === "ArrowUp" && direction != "DOWN") direction = "UP";
                if(event.key === "ArrowDown" && direction != "UP") direction = "DOWN";
                if(event.key === "ArrowLeft" && direction != "RIGHT") direction = "LEFT";
                if(event.key === "ArrowRight" && direction != "LEFT") direction = "RIGHT";
            }});

            // On-screen control buttons
            document.getElementById('btnUp').addEventListener('click', () => {{ if(direction != 'DOWN') direction = 'UP'; }});
            document.getElementById('btnDown').addEventListener('click', () => {{ if(direction != 'UP') direction = 'DOWN'; }});
            document.getElementById('btnLeft').addEventListener('click', () => {{ if(direction != 'RIGHT') direction = 'LEFT'; }});
            document.getElementById('btnRight').addEventListener('click', () => {{ if(direction != 'LEFT') direction = 'RIGHT'; }});

            function draw() {{
                ctx.fillStyle = "black";
                ctx.fillRect(0,0,canvasSize,canvasSize);

                for(let i=0; i<snake.length; i++){{
                    ctx.fillStyle = (i==0) ? "lime" : "green";
                    ctx.fillRect(snake[i].x, snake[i].y, box, box);
                }}

                ctx.fillStyle = "red";
                ctx.fillRect(food.x, food.y, box, box);

                // If not started yet, show countdown overlay and don't move the snake
                if(!started){{
                    ticks++;
                    if(ticks % 5 === 0) {{ countdown--; ticks = 0; }}
                    // Draw overlay
                    ctx.fillStyle = 'rgba(0,0,0,0.6)';
                    ctx.fillRect(0,0,canvasSize,canvasSize);
                    ctx.fillStyle = 'white';
                    ctx.font = '48px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText(countdown > 0 ? countdown : 'Go!', canvasSize/2, canvasSize/2);
                    if(countdown <= 0) started = true;
                    // Still render score in corner
                    ctx.fillStyle = "white";
                    ctx.font = "20px Arial";
                    ctx.fillText("Score: "+score, 10, 20);
                    return;
                }}

                let head = {{x: snake[0].x, y: snake[0].y}};
                if(direction==="UP") head.y -= box;
                if(direction==="DOWN") head.y += box;
                if(direction==="LEFT") head.x -= box;
                if(direction==="RIGHT") head.x += box;

                if(head.x < 0 || head.x >= canvasSize || head.y < 0 || head.y >= canvasSize || collision(head, snake)){{
                    gameOver();
                    return;
                }}

                snake.unshift(head);

                if(head.x === food.x && head.y === food.y){{
                    score++;
                    food = {{x: Math.floor(Math.random()*20)*box, y: Math.floor(Math.random()*20)*box}};
                }} else {{
                    snake.pop();
                }}

                ctx.fillStyle = "white";
                ctx.font = "20px Arial";
                ctx.fillText("Score: "+score, 10, 20);
            }}

            function collision(head, array){{
                for(let i=0;i<array.length;i++){{
                    if(head.x === array[i].x && head.y === array[i].y){{
                        return true;
                    }}
                }}
                return false;
            }}

            function gameOver(){{
                clearInterval(game);
                ctx.fillStyle = 'rgba(0,0,0,0.6)';
                ctx.fillRect(0,0,canvasSize,canvasSize);
                ctx.fillStyle = 'white';
                ctx.font = '28px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('💀 Game Over! Score: ' + score, canvasSize/2, canvasSize/2);
            }}

            let game = setInterval(draw, 200);
        </script>
        """,
        height=450,
    )

    # Remove Streamlit arrow buttons — on-screen HTML buttons are used instead
