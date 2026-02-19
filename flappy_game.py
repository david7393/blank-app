import streamlit as st


def flappy_game():
    """Simple Flappy-like game embedded via HTML/JS canvas.
    Tap/click or press space to make the bird flap.
    """
    html = r"""
    <div style='text-align:center'>
      <canvas id='flappy' width='400' height='300' style='border:1px solid #ccc; background:#87ceeb;'></canvas>
      <div style='margin-top:6px;font-size:12px;color:#333;'>Tap/click or press Space to flap. Pass through gaps to score.</div>
    </div>
    <script>
    const canvas = document.getElementById('flappy');
    const ctx = canvas.getContext('2d');
    let bird = {x:80,y:150,r:12,vy:0,grav:0.6};
    let pipes = [];
    let frame = 0;
    let score = 0;
    let alive = true;

    function spawnPipe(){
      let gap = 90; let top = Math.random()*(canvas.height-200)+20;
      pipes.push({x:canvas.width,y:0,w:40,top:top,gap:gap});
    }

    function flap(){ if(!alive) return; bird.vy = -9; }
    document.addEventListener('keydown', e=>{ if(e.code==='Space') flap(); });
    canvas.addEventListener('click', flap);

    function update(){ if(!alive) return; frame++; if(frame%90===0) spawnPipe(); bird.vy+=bird.grav; bird.y+=bird.vy; if(bird.y+bird.r>canvas.height || bird.y-bird.r<0) alive=false;
      for(let i=pipes.length-1;i>=0;i--){ pipes[i].x-=2.5; if(pipes[i].x + pipes[i].w < 0){ pipes.splice(i,1); score++; } }
      // collisions
      for(let p of pipes){ if(bird.x+bird.r > p.x && bird.x-bird.r < p.x + p.w){ if(bird.y - bird.r < p.top || bird.y + bird.r > p.top + p.gap){ alive=false; } } }
    }

    function draw(){ ctx.clearRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#ffd700'; ctx.fillRect(0,canvas.height-40,canvas.width,40); // ground
      // bird
      ctx.fillStyle='#ff4d4d'; ctx.beginPath(); ctx.arc(bird.x,bird.y,bird.r,0,Math.PI*2); ctx.fill();
      // pipes
      ctx.fillStyle='#228B22'; for(let p of pipes){ ctx.fillRect(p.x,p.top,p.w,p.gap); ctx.fillRect(p.x,p.top+p.gap+60,p.w,canvas.height-(p.top+p.gap+60)-40); }
      ctx.fillStyle='#000'; ctx.font='18px sans-serif'; ctx.fillText('Score: '+score,10,20);
      if(!alive){ ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#fff'; ctx.font='20px sans-serif'; ctx.fillText('Game Over - Refresh to Play Again',30,140); }
    }

    function loop(){ update(); draw(); requestAnimationFrame(loop); }
    loop();
    </script>
    """

    st.components.v1.html(html, height=360)


if __name__ == '__main__':
    flappy_game()
