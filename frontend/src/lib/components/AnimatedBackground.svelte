<script>
  export let variant = 'default';
</script>

<div class="animated-bg {variant}">
  <div class="gradient-layer"></div>
  <div class="pattern-layer"></div>
  <div class="shapes-layer">
    <div class="geometric-shape circle-1"></div>
    <div class="geometric-shape circle-2"></div>
    <div class="geometric-shape circle-3"></div>
    <div class="geometric-shape hexagon-1"></div>
    <div class="geometric-shape hexagon-2"></div>
    <div class="geometric-shape triangle-1"></div>
    <div class="geometric-shape triangle-2"></div>
    <div class="geometric-shape square-1"></div>
    <div class="geometric-shape square-2"></div>
  </div>
  <div class="particles-layer">
    {#each Array(20) as _, i}
      <div class="particle" style="--delay: {i * 0.5}s; --x: {Math.random() * 100}%; --y: {Math.random() * 100}%;"></div>
    {/each}
  </div>
  <div class="overlay-layer"></div>
</div>

<style>
  .animated-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
  }

  .gradient-layer {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    opacity: 0.9;
  }

  .animated-bg.blue .gradient-layer {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
  }

  .animated-bg.green .gradient-layer {
    background: linear-gradient(135deg, #065f46 0%, #10b981 50%, #3b82f6 100%);
  }

  .animated-bg.purple .gradient-layer {
    background: linear-gradient(135deg, #581c87 0%, #9333ea 50%, #ec4899 100%);
  }

  .pattern-layer {
    position: absolute;
    inset: 0;
    background-image: 
      repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,.03) 35px, rgba(255,255,255,.03) 70px),
      repeating-linear-gradient(-45deg, transparent, transparent 35px, rgba(255,255,255,.02) 35px, rgba(255,255,255,.02) 70px);
    animation: patternMove 60s linear infinite;
  }

  .shapes-layer {
    position: absolute;
    inset: 0;
  }

  .geometric-shape {
    position: absolute;
    opacity: 0.1;
    filter: blur(2px);
  }

  .circle-1 {
    width: 300px;
    height: 300px;
    border: 3px solid rgba(255,255,255,0.3);
    border-radius: 50%;
    top: 10%;
    left: 5%;
    animation: float1 25s ease-in-out infinite;
  }

  .circle-2 {
    width: 200px;
    height: 200px;
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 50%;
    top: 60%;
    right: 10%;
    animation: float2 20s ease-in-out infinite;
  }

  .circle-3 {
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
    bottom: 15%;
    left: 50%;
    animation: float3 30s ease-in-out infinite;
  }

  .hexagon-1 {
    width: 100px;
    height: 100px;
    background: rgba(255,255,255,0.05);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    top: 30%;
    right: 20%;
    animation: rotate1 40s linear infinite;
  }

  .hexagon-2 {
    width: 80px;
    height: 80px;
    border: 2px solid rgba(255,255,255,0.15);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    bottom: 25%;
    left: 15%;
    animation: rotate2 35s linear infinite reverse;
  }

  .triangle-1 {
    width: 0;
    height: 0;
    border-left: 75px solid transparent;
    border-right: 75px solid transparent;
    border-bottom: 130px solid rgba(255,255,255,0.08);
    top: 45%;
    left: 25%;
    animation: float1 28s ease-in-out infinite;
  }

  .triangle-2 {
    width: 0;
    height: 0;
    border-left: 50px solid transparent;
    border-right: 50px solid transparent;
    border-bottom: 87px solid rgba(255,255,255,0.06);
    top: 70%;
    right: 30%;
    animation: float2 22s ease-in-out infinite;
  }

  .square-1 {
    width: 120px;
    height: 120px;
    border: 3px solid rgba(255,255,255,0.12);
    top: 15%;
    right: 35%;
    animation: rotate1 45s linear infinite;
  }

  .square-2 {
    width: 90px;
    height: 90px;
    background: rgba(255,255,255,0.04);
    bottom: 30%;
    right: 15%;
    transform: rotate(45deg);
    animation: float3 26s ease-in-out infinite;
  }

  .particles-layer {
    position: absolute;
    inset: 0;
  }

  .particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: rgba(255,255,255,0.6);
    border-radius: 50%;
    left: var(--x);
    top: var(--y);
    animation: particleFloat 15s ease-in-out infinite;
    animation-delay: var(--delay);
    box-shadow: 0 0 10px rgba(255,255,255,0.5);
  }

  .overlay-layer {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 50%, transparent 0%, rgba(0,0,0,0.1) 100%);
  }

  @keyframes patternMove {
    0% { background-position: 0 0; }
    100% { background-position: 100px 100px; }
  }

  @keyframes float1 {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(30px, -40px) rotate(90deg); }
    50% { transform: translate(-20px, 30px) rotate(180deg); }
    75% { transform: translate(40px, 20px) rotate(270deg); }
  }

  @keyframes float2 {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(-40px, 30px) rotate(120deg); }
    66% { transform: translate(30px, -20px) rotate(240deg); }
  }

  @keyframes float3 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(20px, -30px) scale(1.2); }
  }

  @keyframes rotate1 {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  @keyframes rotate2 {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(0deg); }
  }

  @keyframes particleFloat {
    0%, 100% { 
      transform: translate(0, 0);
      opacity: 0;
    }
    10% { opacity: 1; }
    90% { opacity: 1; }
    50% { 
      transform: translate(calc(var(--x) - 50%), calc(var(--y) - 50%));
    }
  }
</style>
