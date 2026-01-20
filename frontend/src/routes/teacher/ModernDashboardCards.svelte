<script>
  import { FileQuestion, Target, CheckCircle, Megaphone, TrendingUp, Users, Award, Clock } from 'lucide-svelte';
  
  export let questions = [];
  export let quizzes = [];
  export let announcements = [];
  export let user;
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  <!-- My Questions Card -->
  <div class="group relative overflow-hidden bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
    <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500"></div>
    <div class="relative z-10">
      <div class="flex items-center justify-between mb-4">
        <div class="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
          <FileQuestion class="w-8 h-8 text-white" strokeWidth={2.5} />
        </div>
        <TrendingUp class="w-6 h-6 text-white/60 group-hover:text-white transition-colors" />
      </div>
      <div class="text-4xl font-black text-white mb-2">
        {questions.filter(q => q.created_by === user?.id).length}
      </div>
      <div class="text-blue-100 font-semibold text-sm uppercase tracking-wide">My Questions</div>
      <div class="mt-3 h-1 w-16 bg-white/30 rounded-full group-hover:w-full transition-all duration-500"></div>
    </div>
  </div>

  <!-- My Quizzes Card -->
  <div class="group relative overflow-hidden bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
    <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500"></div>
    <div class="relative z-10">
      <div class="flex items-center justify-between mb-4">
        <div class="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
          <Target class="w-8 h-8 text-white" strokeWidth={2.5} />
        </div>
        <Award class="w-6 h-6 text-white/60 group-hover:text-white transition-colors" />
      </div>
      <div class="text-4xl font-black text-white mb-2">
        {quizzes.filter(q => q.created_by === user?.id).length}
      </div>
      <div class="text-purple-100 font-semibold text-sm uppercase tracking-wide">My Quizzes</div>
      <div class="mt-3 h-1 w-16 bg-white/30 rounded-full group-hover:w-full transition-all duration-500"></div>
    </div>
  </div>

  <!-- Active Quizzes Card -->
  <div class="group relative overflow-hidden bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
    <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500"></div>
    <div class="relative z-10">
      <div class="flex items-center justify-between mb-4">
        <div class="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
          <CheckCircle class="w-8 h-8 text-white" strokeWidth={2.5} />
        </div>
        <Clock class="w-6 h-6 text-white/60 group-hover:text-white transition-colors animate-pulse" />
      </div>
      <div class="text-4xl font-black text-white mb-2">
        {quizzes.filter(q => q.is_active && q.created_by === user?.id).length}
      </div>
      <div class="text-green-100 font-semibold text-sm uppercase tracking-wide">Active Quizzes</div>
      <div class="mt-3 h-1 w-16 bg-white/30 rounded-full group-hover:w-full transition-all duration-500"></div>
    </div>
  </div>

  <!-- Announcements Card -->
  <div class="group relative overflow-hidden bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
    <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500"></div>
    <div class="relative z-10">
      <div class="flex items-center justify-between mb-4">
        <div class="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
          <Megaphone class="w-8 h-8 text-white" strokeWidth={2.5} />
        </div>
        <Users class="w-6 h-6 text-white/60 group-hover:text-white transition-colors" />
      </div>
      <div class="text-4xl font-black text-white mb-2">
        {announcements.length}
      </div>
      <div class="text-orange-100 font-semibold text-sm uppercase tracking-wide">Announcements</div>
      <div class="mt-3 h-1 w-16 bg-white/30 rounded-full group-hover:w-full transition-all duration-500"></div>
    </div>
  </div>
</div>

<style>
  @keyframes float {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-10px);
    }
  }
  
  .group:hover {
    animation: float 2s ease-in-out infinite;
  }
</style>
