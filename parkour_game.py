import streamlit as st


def parkour_game():
    """Very simple parkour game embedded as HTML/JS using a canvas.
    Controls: tap/click or press space to jump.
    This is intentionally minimal and uses plain JS for easy embedding.
    """
    html = r"""
    <div style='text-align:center'>
      <canvas id='parkour' width='480' height='200' style='border:1px solid #ccc; background:#eaf6ff;'></canvas>
      <div style='margin-top:6px;font-size:12px;color:#333;'>Tap/click or press Space to jump. Survive as long as possible.</div>
    </div>
    <script>
    const canvas = document.getElementById('parkour');
    const ctx = canvas.getContext('2d');
    let player = {x:50,y:150,w:20,h:30,vy:0,grav:0.9,ground:170};
    let obstacles = [];
    let speed = 3;
    let tick = 0;
    let alive = true;

    function spawn(){
      const h = 20 + Math.random()*40;
      obstacles.push({x:480,y:170-h,w:20,h:h});
    }

    function jump(){
      if(!alive) return; if(player.y>=player.ground){ player.vy = -12; }
    }

    document.addEventListener('keydown', e=>{ if(e.code==='Space') jump(); });
    canvas.addEventListener('click', jump);

    function update(){
      if(!alive) return;
      tick++;
      if(tick%90===0){ spawn(); }
      if(tick%600===0){ speed += 0.5; }

      player.vy += player.grav; player.y += player.vy;
      if(player.y > player.ground) { player.y = player.ground; player.vy = 0; }

      for(let i=obstacles.length-1;i>=0;i--){
        obstacles[i].x -= speed;
        if(obstacles[i].x + obstacles[i].w < 0) obstacles.splice(i,1);
        // collision
        if(player.x < obstacles[i].x + obstacles[i].w && player.x + player.w > obstacles[i].x && player.y < obstacles[i].y + obstacles[i].h && player.y + player.h > obstacles[i].y){
          alive = false;
        }
      }
    }

    function draw(){
      ctx.clearRect(0,0,canvas.width,canvas.height);
      // ground
      ctx.fillStyle = '#88c070'; ctx.fillRect(0,170,canvas.width,30);
      // player
      ctx.fillStyle = '#333'; ctx.fillRect(player.x, player.y-player.h, player.w, player.h);
      // obstacles
      ctx.fillStyle = '#b33';
      obstacles.forEach(o=> ctx.fillRect(o.x, o.y, o.w, o.h));
      if(!alive){ ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#fff'; ctx.font='20px sans-serif'; ctx.fillText('Game Over - Refresh to Play Again',40,100); }
    }

    function loop(){ update(); draw(); requestAnimationFrame(loop); }
    loop();
    </script>
    """

    st.components.v1.html(html, height=300)


if __name__ == '__main__':
    parkour_game()
