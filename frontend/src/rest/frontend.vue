<template>
  <div class="frontend-container">
    <Navigation_bar></Navigation_bar>
    
    <transition name="route" mode="out-in">
      <router-view id="route"></router-view>
    </transition>

    <footer>
      <p>PBOJ</p>
    </footer>
  </div>
</template>

<script>
import Navigation_bar from "@/rest/Navigation_bar.vue";

export default {
  name: 'frontend',
  components: {
    Navigation_bar
  }
}
</script>


<style>

*{
  margin: 0;
  padding: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
  /* overflow: hidden; */
}
footer{
  margin-top: 20px;
  margin-bottom: 10px;
  text-align: center;
  font-size: small;
}

/* 路由过渡动画 */
.route-enter-active {
  transition: opacity 0.25s ease 0.15s;
}
.route-leave-active {
  transition: opacity 0.25s ease;
}

.route-enter-from,
.route-leave-to {
  opacity: 0;
}

/* 可以添加另一种过渡效果 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* .fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
} */
/* .fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ 
  /* opacity: 0; */

</style>
