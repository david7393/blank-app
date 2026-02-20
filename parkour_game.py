import streamlit as st


def parkour_game():
    """Very simple parkour game embedded as HTML/JS using a canvas.
    Controls: tap/click or press space to jump.
    Features 5-second countdown, improved character graphics, and increasing difficulty.
    """
    html = r"""
    <div style='text-align:center'>
      <canvas id='parkour' width='640' height='300' style='border:1px solid #ccc; background:#eaf6ff;'></canvas>
      <div style='margin-top:6px;font-size:12px;color:#333;'>Tap/click or press Space to jump. Survive as long as possible.</div>
    </div>
    <script>
    const canvas = document.getElementById('parkour');
    const ctx = canvas.getContext('2d');
    let player = {x:50,y:220,w:20,h:30,vy:0,grav:0.9,ground:250};
    let obstacles = [];
    let speed = 1.5;
    let tick = 0;
    let alive = true;
    let gameStarted = false;
    let countdownTime = 5;

    function spawn(){
      const h = 20 + Math.random()*40;
      obstacles.push({x:640,y:250-h,w:20,h:h});
    }

    function jump(){
      if(!alive) return; if(player.y>=player.ground){ player.vy = -12; }
    }

    document.addEventListener('keydown', e=>{ if(e.code==='Space') jump(); });
    canvas.addEventListener('click', jump);

    function update(){
      if(!alive) return;
      if(tick%90===0){ spawn(); }
      if(tick%600===0){ speed += 0.2; }

      player.vy += player.grav; player.y += player.vy;
      if(player.y > player.ground) { player.y = player.ground; player.vy = 0; }

      for(let i=obstacles.length-1;i>=0;i--){
        obstacles[i].x -= speed;
        if(obstacles[i].x + obstacles[i].w < 0) obstacles.splice(i,1);
        // collision - check visual bounds where player is drawn from (y - h) to y
        if(player.x < obstacles[i].x + obstacles[i].w && player.x + player.w > obstacles[i].x && player.y > obstacles[i].y && player.y - player.h < obstacles[i].y + obstacles[i].h){
          alive = false;
        }
      }
    }

    function drawPlayer(){
      // Draw a simple character with head and body
      ctx.fillStyle = '#ff6b6b';
      // Head
      ctx.beginPath();
      ctx.arc(player.x + player.w/2, player.y - player.h + 8, 6, 0, Math.PI*2);
      ctx.fill();
      // Body
      ctx.fillRect(player.x + 6, player.y - player.h + 15, 8, 12);
      // Eyes
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(player.x + player.w/2 - 2, player.y - player.h + 6, 2, 0, Math.PI*2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(player.x + player.w/2 + 2, player.y - player.h + 6, 2, 0, Math.PI*2);
      ctx.fill();
    }

    function draw(){
      ctx.clearRect(0,0,canvas.width,canvas.height);
      // ground
      ctx.fillStyle = '#88c070'; ctx.fillRect(0,170,canvas.width,30);
      // player with better graphics
      drawPlayer();
      // obstacles
      ctx.fillStyle = '#b33';
      obstacles.forEach(o=> ctx.fillRect(o.x, o.y, o.w, o.h));
      // Countdown or game info
      ctx.fillStyle = '#333'; ctx.font='16px sans-serif';
      if(!gameStarted){ ctx.fillText('Starting in: '+countdownTime, 10, 30); }
      else { ctx.fillText('Score: '+Math.floor(tick/10), 10, 30); }
      if(!alive){ ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#fff'; ctx.font='20px sans-serif'; ctx.fillText('Game Over - Refresh to Play Again',40,100); }
    }

    function loop(){
      if(!gameStarted){
        if(tick % 60 === 0){ countdownTime--; }
        if(countdownTime <= 0){ gameStarted = true; tick=0; }
        draw();
      } else {
        update();
        draw();
      }
      tick++;
      requestAnimationFrame(loop);
    }
    loop();
    </script>
    """

    st.components.v1.html(html, height=420)


if __name__ == '__main__':
    parkour_game()
