import streamlit as st


def flappy_game():
    """Simple Flappy-like game embedded via HTML/JS canvas.
    Tap/click or press space to make the bird flap.
    Features 5-second countdown and improved bird graphics.
    Slower movement speed than parkour for easier gameplay.
    """
    html = r"""
    <div style='text-align:center'>
      <canvas id='flappy' width='540' height='360' style='border:1px solid #ccc; background:#87ceeb;'></canvas>
      <div style='margin-top:6px;font-size:12px;color:#333;'>Tap/click or press Space to flap. Pass through gaps to score.</div>
    </div>
    <script>
    const canvas = document.getElementById('flappy');
    const ctx = canvas.getContext('2d');
    let bird = {x:80,y:180,r:12,vy:0,grav:0.4};
    let pipes = [];
    let frame = 0;
    let score = 0;
    let alive = true;
    let gameStarted = false;
    let countdownTime = 5;

    function spawnPipe(){
      let gap = 120; let top = Math.random()*(canvas.height-280)+40;
      pipes.push({x:canvas.width,y:0,w:40,top:top,gap:gap});
    }

    function flap(){ if(!alive || !gameStarted) return; bird.vy = -7; }
    document.addEventListener('keydown', e=>{ if(e.code==='Space') flap(); });
    canvas.addEventListener('click', flap);

    function drawBird(){
      ctx.save();
      ctx.translate(bird.x, bird.y);
      // Body (yellow ellipse)
      ctx.fillStyle = '#ffd700';
      ctx.beginPath();
      ctx.ellipse(0, 0, 14, 10, 0, 0, Math.PI*2);
      ctx.fill();
      // Wing
      ctx.fillStyle = '#ffaa00';
      ctx.beginPath();
      ctx.ellipse(6, 2, 6, 4, -0.3, 0, Math.PI*2);
      ctx.fill();
      // Eye
      ctx.fillStyle = '#000';
      ctx.beginPath();
      ctx.arc(5, -2, 2, 0, Math.PI*2);
      ctx.fill();
      // Beak
      ctx.fillStyle = '#ff6b35';
      ctx.beginPath();
      ctx.moveTo(10, -1);
      ctx.lineTo(14, 0);
      ctx.lineTo(10, 1);
      ctx.fill();
      ctx.restore();
    }

    function update(){ if(!alive || !gameStarted) return; frame++; if(frame%120===0) spawnPipe(); bird.vy+=bird.grav; bird.y+=bird.vy; if(bird.y+bird.r>canvas.height || bird.y-bird.r<0) alive=false;
      for(let i=pipes.length-1;i>=0;i--){ pipes[i].x-=1.2; if(pipes[i].x + pipes[i].w < 0){ pipes.splice(i,1); score++; } }
      // collisions
      for(let p of pipes){ if(bird.x+bird.r > p.x && bird.x-bird.r < p.x + p.w){ if(bird.y - bird.r < p.top || bird.y + bird.r > p.top + p.gap){ alive=false; } } }
      if(bird.y > canvas.height - 50) alive = false;
    }

    function draw(){
      ctx.clearRect(0,0,canvas.width,canvas.height);
      ctx.fillStyle='#ffd700';
      ctx.fillRect(0,canvas.height-50,canvas.width,50); // ground
      // bird with better graphics
      drawBird();
      // pipes
      ctx.fillStyle='#228B22';
      for(let p of pipes){
        ctx.fillRect(p.x,p.top,p.w,p.gap);
        ctx.fillRect(p.x,p.top+p.gap+80,p.w,canvas.height-(p.top+p.gap+80)-50);
      }
      // Score and countdown
      ctx.fillStyle='#000';
      ctx.font='18px sans-serif';
      if(!gameStarted){ ctx.fillText('Starting in: '+countdownTime, 10, 30); }
      else { ctx.fillText('Score: '+score, 10, 30); }
      if(!alive){
        ctx.fillStyle='rgba(0,0,0,0.6)';
        ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle='#fff';
        ctx.font='20px sans-serif';
        ctx.fillText('Game Over - Refresh to Play Again',80,170);
      }
    }

    function loop(){
      if(!gameStarted){
        if(frame % 60 === 0){ countdownTime--; }
        if(countdownTime <= 0){ gameStarted = true; frame=0; }
        draw();
      } else {
        update();
        draw();
      }
      frame++;
      requestAnimationFrame(loop);
    }
    loop();
    </script>
    """

    st.components.v1.html(html, height=420)


if __name__ == '__main__':
    flappy_game()
