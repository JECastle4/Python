import { mount } from '@vue/test-utils';
import DateRangePicker from './DateRangePicker.vue';

describe('DateRangePicker', () => {
  it('emits dateRangeChanged when Apply is clicked', async () => {
    const wrapper = mount(DateRangePicker, {
        props: {
            initialStartDate: '2026-02-01',
            initialEndDate: '2026-02-07'
        }
    });
    // Set a valid date range
    //await wrapper.setData({ startDate: '2026-02-01', endDate: '2026-02-07' });
    // Find and click the Apply button
    const applyBtn = wrapper.find('button');
    await applyBtn.trigger('click');
    await wrapper.vm.$nextTick();
    // Check emitted event
    const emitted = wrapper.emitted('update:dates');
    expect(emitted).toBeTruthy();
    const eventPayload = emitted && emitted[0] && emitted[0][0] as { start: Date; end: Date } | undefined;
    expect(eventPayload).not.toBeNull();
    expect(eventPayload).not.toBeUndefined();
    expect(eventPayload && eventPayload.start).toEqual(new Date('2026-02-01'));
    expect(eventPayload && eventPayload.end).toEqual(new Date('2026-02-07'));
  });
});
