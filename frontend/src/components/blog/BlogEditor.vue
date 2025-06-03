<template>
	<div class="containers">
		<div v-html="announcement" class="ck-content ck-editor" id="editor"></div>
		<div class="list-container">
			
		</div>
	</div>
</template>
<script>
import home_api from "@/api/home/home.js";
import '@ckeditor/ckeditor5-build-classic/build/translations/zh-cn.js';
export default {
	name: "Home",
	data() {
		return {
			announcement: "",
		};
	},
	created() {
		home_api.getAnnouncements().then((res) => {
			const content = res.data.data.announcements[1].content;
			// 替换图片路径
			this.announcement = content.replace(
				/src="\/media\//g,
				'src="http://localhost:8000/media/'
			);
		});
	},
};
</script>
<style>
/* @import '@ckeditor/ckeditor5-build-classic/build/translations/zh-cn.js'; */

.containers {
	overflow: hidden;
	padding: 40px;
}


</style>
