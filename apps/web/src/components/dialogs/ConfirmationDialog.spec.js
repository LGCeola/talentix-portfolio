import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ConfirmationDialog from './ConfirmationDialog.vue'

// O el-dialog real é teleportado para o <body>; aqui ele vira uma div simples com os três slots.
const stubs = {
  'el-dialog': {
    props: ['modelValue', 'beforeClose'],
    template: '<div class="el-dialog"><slot name="header" /><slot /><slot name="footer" /></div>',
  },
  'el-button': {
    props: ['type', 'loading', 'disabled'],
    emits: ['click'],
    template: '<button :class="type" :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
  },
}

function mountDialog(props = {}, slots = {}) {
  return mount(ConfirmationDialog, { props: { modelValue: true, ...props }, slots, global: { stubs } })
}

describe('ConfirmationDialog', () => {
  it('mostra o título, a mensagem e os textos dos botões', () => {
    const wrapper = mountDialog({ title: 'Excluir conta', message: 'Tem certeza?', confirmText: 'Excluir', cancelText: 'Voltar' })

    expect(wrapper.find('.confirmation-title').text()).toBe('Excluir conta')
    expect(wrapper.find('.confirmation-message').text()).toBe('Tem certeza?')
    expect(wrapper.findAll('button').map((button) => button.text())).toEqual(['Voltar', 'Excluir'])
  })

  it('aceita uma mensagem formatada pelo slot', () => {
    const wrapper = mountDialog({}, { default: '<p>Excluir <strong>Vaga X</strong>?</p>' })
    expect(wrapper.find('strong').text()).toBe('Vaga X')
    expect(wrapper.find('.confirmation-message').exists()).toBe(false)
  })

  it('usa a cor de perigo quando danger está ligado', () => {
    const wrapper = mountDialog({ danger: true })
    expect(wrapper.find('.confirmation-icon').classes()).toContain('is-danger')
    expect(wrapper.find('button.danger').exists()).toBe(true)
  })

  it('usa a cor principal por padrão', () => {
    const wrapper = mountDialog()
    expect(wrapper.find('.confirmation-icon').classes()).toContain('is-primary')
    expect(wrapper.find('button.primary').exists()).toBe(true)
  })

  it('emite confirm ao confirmar', async () => {
    const wrapper = mountDialog()
    await wrapper.find('button.primary').trigger('click')
    expect(wrapper.emitted('confirm')).toHaveLength(1)
  })

  it('fecha e emite cancel ao cancelar', async () => {
    const wrapper = mountDialog()
    await wrapper.findAll('button')[0].trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([[false]])
    expect(wrapper.emitted('cancel')).toHaveLength(1)
  })

  it('não fecha enquanto a ação está carregando', () => {
    const wrapper = mountDialog({ loading: true })
    wrapper.findComponent(stubs['el-dialog']).props('beforeClose')()
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
    expect(wrapper.emitted('cancel')).toBeUndefined()
  })
})
