<template>
  <div ref="editorContainer" class="monaco-editor"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps({
  value: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'cpp'
  },
  theme: {
    type: String,
    default: 'vs'
  },
  options: {
    type: Object,
    default: () => ({
      automaticLayout: true,
      scrollBeyondLastLine: false,
      minimap: { enabled: true },
      folding: true,
      foldingStrategy: 'auto'
    })
  }
})

const emit = defineEmits(['update:value', 'change'])
const editorContainer = ref(null)
let editor = null

onMounted(() => {
  editor = monaco.editor.create(editorContainer.value, {
    value: props.value,
    language: props.language,
    theme: props.theme,
    ...props.options
  })

  editor.onDidChangeModelContent(() => {
    const value = editor.getValue()
    emit('update:value', value)
    emit('change', value)
  })
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
  }
})

watch(() => props.value, (newValue) => {
  if (editor && newValue !== editor.getValue()) {
    editor.setValue(newValue)
  }
})

watch(() => props.language, (newValue) => {
  if (editor) {
    monaco.editor.setModelLanguage(editor.getModel(), newValue)
  }
})
</script>

<style scoped>
.monaco-editor {
  width: 100%;
  height: 100%;
}
</style> 