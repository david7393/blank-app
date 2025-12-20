import streamlit as st
import streamlit.components.v1 as components

def snake_game():
    st.header("🎮 Reward Snake Game")
    st.write("Use arrow keys or on-screen buttons to control the snake. 🍎")

    # Direction controls via buttons
    cols = st.columns(3)
    if cols[1].button("⬆️") and st.session_state.get("direction", "RIGHT") != "DOWN":
        st.session_state.direction = "UP"
    cols = st.columns(3)
    if cols[0].button("⬅️") and st.session_state.get("direction", "RIGHT") != "RIGHT":
        st.session_state.direction = "LEFT"
    if cols[2].button("➡️") and st.session_state.get("direction", "RIGHT") != "LEFT":
        st.session_state.direction = "RIGHT"
    cols = st.columns(3)
    if cols[1].button("⬇️") and st.session_state.get("direction", "RIGHT") != "UP":
        st.session_state.direction = "DOWN"

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
        <script>
            const canvas = document.getElementById("snakeCanvas");
            const ctx = canvas.getContext("2d");
            const box = 20;
            const canvasSize = 400;

            let snake = [{x: 9*box, y: 9*box}];
            let food = {{x: Math.floor(Math.random()*20)*box, y: Math.floor(Math.random()*20)*box}};
            let direction = "{st.session_state.direction}";
            let score = 0;

            // Arrow keys for JS (optional if using Python buttons)
            document.addEventListener("keydown", function(event){{
                if(event.key === "ArrowUp" && direction != "DOWN") direction = "UP";
                if(event.key === "ArrowDown" && direction != "UP") direction = "DOWN";
                if(event.key === "ArrowLeft" && direction != "RIGHT") direction = "LEFT";
                if(event.key === "ArrowRight" && direction != "LEFT") direction = "RIGHT";
            }});

            function draw() {{
                ctx.fillStyle = "black";
                ctx.fillRect(0,0,canvasSize,canvasSize);

                for(let i=0; i<snake.length; i++){{
                    ctx.fillStyle = (i==0) ? "lime" : "green";
                    ctx.fillRect(snake[i].x, snake[i].y, box, box);
                }}

                ctx.fillStyle = "red";
                ctx.fillRect(food.x, food.y, box, box);

                let head = {{x: snake[0].x, y: snake[0].y}};
                if(direction==="UP") head.y -= box;
                if(direction==="DOWN") head.y += box;
                if(direction==="LEFT") head.x -= box;
                if(direction==="RIGHT") head.x += box;

                if(head.x < 0 || head.x >= canvasSize || head.y < 0 || head.y >= canvasSize || collision(head, snake)){{
                    clearInterval(game);
                    alert("💀 Game Over! Score: " + score);
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

            let game = setInterval(draw, 200);
        </script>
        """,
        height=450,
    )
