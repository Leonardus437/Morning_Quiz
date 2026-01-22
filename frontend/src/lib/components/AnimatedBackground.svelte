<script>
  export let variant = 'default';
</script>

<div class="animated-bg {variant}">
  <div class="gradient-orb orb-1"></div>
  <div class="gradient-orb orb-2"></div>
  <div class="gradient-orb orb-3"></div>
  <div class="floating-shapes">
    <div class="shape shape-1"></div>
    <div class="shape shape-2"></div>
    <div class="shape shape-3"></div>
    <div class="shape shape-4"></div>
  </div>
</div>

<style>
  .animated-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
  }

  .gradient-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.3;
    animation: float 20s ease-in-out infinite;
  }

  .orb-1 {
    width: 500px;
    height: 500px;
    top: -250px;
    left: -250px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.5) 0%, transparent 70%);
    animation-delay: 0s;
  }

  .orb-2 {
    width: 400px;
    height: 400px;
    top: 50%;
    right: -200px;
    background: radial-gradient(circle, rgba(147, 51, 234, 0.4) 0%, transparent 70%);
    animation-delay: 7s;
  }

  .orb-3 {
    width: 600px;
    height: 600px;
    bottom: -300px;
    left: 30%;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.3) 0%, transparent 70%);
    animation-delay: 14s;
  }

  .animated-bg.blue .orb-1 { background: radial-gradient(circle, rgba(59, 130, 246, 0.6) 0%, transparent 70%); }
  .animated-bg.blue .orb-2 { background: radial-gradient(circle, rgba(96, 165, 250, 0.5) 0%, transparent 70%); }
  .animated-bg.blue .orb-3 { background: radial-gradient(circle, rgba(37, 99, 235, 0.4) 0%, transparent 70%); }

  .animated-bg.purple .orb-1 { background: radial-gradient(circle, rgba(147, 51, 234, 0.6) 0%, transparent 70%); }
  .animated-bg.purple .orb-2 { background: radial-gradient(circle, rgba(168, 85, 247, 0.5) 0%, transparent 70%); }
  .animated-bg.purple .orb-3 { background: radial-gradient(circle, rgba(126, 34, 206, 0.4) 0%, transparent 70%); }

  .animated-bg.green .orb-1 { background: radial-gradient(circle, rgba(16, 185, 129, 0.6) 0%, transparent 70%); }
  .animated-bg.green .orb-2 { background: radial-gradient(circle, rgba(52, 211, 153, 0.5) 0%, transparent 70%); }
  .animated-bg.green .orb-3 { background: radial-gradient(circle, rgba(5, 150, 105, 0.4) 0%, transparent 70%); }

  .floating-shapes {
    position: absolute;
    inset: 0;
  }

  .shape {
    position: absolute;
    opacity: 0.05;
    animation: float 15s ease-in-out infinite;
  }

  .shape-1 {
    width: 100px;
    height: 100px;
    top: 20%;
    left: 10%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
    animation-delay: 0s;
  }

  .shape-2 {
    width: 150px;
    height: 150px;
    top: 60%;
    right: 15%;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 63% 37% 54% 46% / 55% 48% 52% 45%;
    animation-delay: 5s;
  }

  .shape-3 {
    width: 80px;
    height: 80px;
    bottom: 20%;
    left: 60%;
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 40% 60% 60% 40% / 60% 30% 70% 40%;
    animation-delay: 10s;
  }

  .shape-4 {
    width: 120px;
    height: 120px;
    top: 40%;
    right: 40%;
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%;
    animation-delay: 3s;
  }

  @keyframes float {
    0%, 100% {
      transform: translate(0, 0) rotate(0deg) scale(1);
    }
    25% {
      transform: translate(30px, -30px) rotate(90deg) scale(1.1);
    }
    50% {
      transform: translate(-20px, 20px) rotate(180deg) scale(0.9);
    }
    75% {
      transform: translate(40px, 10px) rotate(270deg) scale(1.05);
    }
  }
</style>
