<template>
  <div>
    <div id='d3div' ref='d3div'></div>
    <!-- <div class='footer'>
      <v-btn
        :to='"/admin/" + this.$route.params.db_name + "/grids/" + defaultGridDbName'
        class='constructor-button'
        flat
        small
      >
        &nbsp;
        <b>Next</b> &nbsp;
        <i class='fas fa-arrow-right'></i> &nbsp;
        build Grids
        &nbsp;
        <i class='fas fa-columns'></i>
      </v-btn>
    </div>-->
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'WorkflowConstructorContent',
  data: () => ({
    ax_states: null,
    ax_actions: null,
    container_margin: null,
    container_width: null,
    container_height: null,
    BOX_WIDTH: 200,
    BOX_HEIGHT: 40,
    BOX_TOP_MARGIN: 0,
    BOX_RADIUS: 20,
    WRAP_LINE_HEIGHT: 35,
    NEW_ACTION_TIMEOUT: 150,
    state_mouse_down_timestamp: null,
    action_mousedown_position: null,
    diagram_action_mode: false,
    new_action_from_id: null,
    new_action_to_state_id: null,
    change_radius_action_id: null,
    change_starting_radius: null,
    selected_state_id: null,
    selected_action_id: null,
    drag_start_position: {},
    zoom: null,
    drag: null,
    svg: null,
    global_g: null,
    global_rect: null,
    container: null,
    d3_actions: null,
    d3_states: null,
    new_action_line: null
  }),
  computed: {
    defaultGridDbName() {
      const defaultGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      return defaultGrid ? defaultGrid.dbName : null;
    }
  },
  mounted() {
    this.initD3();
  },
  methods: {
    initD3() {
      this.initData();
      this.initZoom();
      this.initDrag();
      this.initSvg();

      this.redraw_states();
      this.draw_start();
      this.draw_end();
      this.draw_all();
      this.redraw_actions();
    },

    initData() {
      this.ax_states = [
        {
          id: 401,
          x: 43,
          y: 67,
          name: 'first',
          type: 1
        },
        {
          id: 402,
          x: 340,
          y: 150,
          name: 'second',
          type: 1
        },
        {
          id: 403,
          x: 500,
          y: 450,
          name: 'third',
          type: 1
        },
        {
          id: 404,
          x: 600,
          y: 520,
          name: 'fourth',
          type: 1
        },
        {
          id: 405,
          x: 700,
          y: 150,
          name: 'fifth',
          type: 1
        },
        {
          id: 406,
          x: 900,
          y: 370,
          name:
            'Very big name with many words Very big name with many words Very big name with many words',
          type: 1
        },
        {
          id: 407,
          x: 700,
          y: 150,
          name: 'Start',
          type: 2
        },
        {
          id: 408,
          x: 700,
          y: 250,
          name: 'Deleted',
          type: 3
        },
        {
          id: 409,
          x: 700,
          y: 350,
          name: 'All',
          type: 4
        }
      ];

      this.ax_actions = [
        {
          id: 900,
          from_state_id: 401,
          to_state_id: 402,
          name: 'First action',
          radius: 0
        },
        {
          id: 901,
          from_state_id: 402,
          to_state_id: 401,
          name: 'First action',
          radius: 0
        },
        {
          id: 902,
          from_state_id: 404,
          to_state_id: 401,
          name: 'First action',
          radius: 500
        },
        {
          id: 903,
          from_state_id: 404,
          to_state_id: 405,
          name: 'First action',
          radius: 0
        },
        {
          id: 904,
          from_state_id: 402,
          to_state_id: 406,
          name: 'Second action',
          radius: 0
        },
        {
          id: 905,
          from_state_id: 401,
          to_state_id: 401,
          name: 'Update 1',
          radius: 0
        },
        {
          id: 906,
          from_state_id: 402,
          to_state_id: 402,
          name: 'Update 2',
          radius: 0
        },
        {
          id: 907,
          from_state_id: 403,
          to_state_id: 403,
          name: 'Update 3',
          radius: 0
        },
        {
          id: 908,
          from_state_id: 404,
          to_state_id: 404,
          name: 'Update 4',
          radius: 0
        },
        {
          id: 909,
          from_state_id: 405,
          to_state_id: 405,
          name: 'Update 5',
          radius: 0
        },
        {
          id: 910,
          from_state_id: 406,
          to_state_id: 406,
          name: 'Update 6.1',
          radius: 0
        },
        {
          id: 911,
          from_state_id: 406,
          to_state_id: 406,
          name: 'Update 6.2',
          radius: 0
        },
        {
          id: 912,
          from_state_id: 406,
          to_state_id: 406,
          name: 'Update 6.3',
          radius: 0
        },
        {
          id: 913,
          from_state_id: 406,
          to_state_id: 406,
          name: 'Update 6.4',
          radius: 0
        },
        {
          id: 914,
          from_state_id: 407,
          to_state_id: 405,
          name: 'Start action',
          radius: 0
        }
      ];

      window.addEventListener('keyup', this.check_delete);

      this.container_margin = {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      };
      this.container_width =
        1400 - this.container_margin.left - this.container_margin.right;
      this.container_height =
        900 - this.container_margin.top - this.container_margin.bottom;
    },
    initZoom() {
      this.zoom = d3
        .zoom()
        .scaleExtent([0.2, 1])
        .on('zoom', () => {
          const global_g = d3.select(document.getElementById('global_g'));
          global_g.attr('transform', d3.event.transform);
        });
    },
    initDrag() {
      this.drag = d3
        .drag()
        .subject(d => d)
        .on('start', d => {
          d3.event.sourceEvent.stopPropagation();
          this.drag_start_position.x = d3.event.x;
          this.drag_start_position.y = d3.event.y;
        })
        .on('drag', (d, i, nodes) => {
          let element_is_dragged = false;
          if (
            d3.event.x != this.drag_start_position.x ||
            d3.event.y != this.drag_start_position.y
          ) {
            element_is_dragged = true;
          }

          // If user is holding mouse for some time - it is action mode (create action or change radius)
          const timeDelta = new Date() - this.state_mouse_down_timestamp;
          this.diagram_action_mode = !(
            this.state_mouse_down_timestamp != null &&
            timeDelta < this.NEW_ACTION_TIMEOUT
          );
          if (element_is_dragged) this.state_mouse_down_timestamp = null;

          if (this.diagram_action_mode && this.new_action_from_id) {
            const currentState = nodes[i];
            const mouse_position = d3.mouse(currentState);
            this.handle_new_action_drag(d, mouse_position);
          } else if (this.diagram_action_mode && this.change_radius_action_id) {
            const global_g = document.getElementById('global_g');
            const mouse_position = d3.mouse(global_g);
            this.handle_radius_changle_drag(d, mouse_position);
          } else if (element_is_dragged) {
            this.diagram_action_mode = false;
            this.new_action_from_id = null;
            this.handle_state_drag(d);
          }
        })
        .on('end', d => {
          if (this.diagram_action_mode && this.new_action_from_id) {
            this.handle_new_action_dragend(d);
          } else {
            this.diagram_action_mode = false;
            this.change_radius_action_id = null;
            this.action_mousedown_position = null;
          }
        });
    },
    initSvg() {
      this.svg = d3
        .select('#d3div')
        .append('svg')
        .attr(
          'width',
          this.container_width +
            this.container_margin.left +
            this.container_margin.right
        )
        .attr(
          'height',
          this.container_height +
            this.container_margin.top +
            this.container_margin.bottom
        )
        .append('g')
        .attr(
          'transform',
          `translate(${this.container_margin.left},${
            this.container_margin.right
          })`
        )
        .call(this.zoom);

      // Declare actions arrow marker
      this.svg
        .append('defs')
        .selectAll('marker')
        .data(this.ax_actions)
        .enter()
        .append('marker')
        .attr('id', d => 'd3_marker')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 10)
        .attr('markerWidth', 10)
        .attr('markerHeight', 10)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('class', 'end-arrow');

      // declare  new action marker
      this.svg
        .append('defs')
        .selectAll('marker')
        .data(this.ax_actions)
        .enter()
        .append('marker')
        .attr('id', 'd3_new_action_marker')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 10)
        .attr('markerWidth', 10)
        .attr('markerHeight', 10)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('class', 'new-action-arrow');

      // Declare global rect. It is used for zooming and panning
      this.global_rect = this.svg
        .append('rect')
        .attr('width', this.container_width)
        .attr('height', this.container_height)
        .style('fill', 'none')
        .style('pointer-events', 'all')
        .attr('id', 'global_rect')
        .on('dblclick', this.handle_create_state)
        .on('mousemove', d => {});

      // Decalre container g - it holds all states and actions
      this.container = this.svg
        .append('g')
        .attr('id', 'global_g')
        .on('mousemove', () => {});

      //  Declare actions array and bind it to ax_actions data
      this.d3_actions = this.container
        .append('g')
        .selectAll('g.d3_action_g')
        .data(
          this.ax_actions.filter(
            action => action.to_state_id != action.from_state_id
          )
        );

      //  Declare states array and bind it to ax_states data
      this.d3_states = this.container
        .append('g')
        .selectAll('g.g_state')
        .data(this.ax_states);

      // New action line - is vissible only on action creation
      this.new_action_line = this.container
        .append('line')
        .attr('class', 'd3_new_action hidden')
        .attr('id', 'd3_new_action')
        .attr('marker-end', (d, i) => 'url(#d3_new_action_marker)')
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', 0)
        .attr('y2', 0);

      this.svg.on('dblclick.zoom', null); // Disable double click for zoom
    },

    handle_new_action_drag(d, mouse_position) {
      const state_x = d.x;
      const state_y = d.y;
      const action_line = d3.select('#d3_new_action');
      action_line
        .classed('hidden', false)
        .attr('x1', state_x)
        .attr('y1', state_y + this.BOX_HEIGHT / 2)
        .attr('x2', state_x + mouse_position[0])
        .attr('y2', state_y + mouse_position[1]);

      const current_state = d3.select(`#d3_rect_${d.id}`);
      current_state.classed('d3_new_action_state', true);
    },

    handle_new_action_dragend(d) {
      const action_line = d3.select('#d3_new_action');
      action_line.classed('hidden', true);
      const from_state = d3.select(`#d3_rect_${d.id}`);
      from_state.classed('d3_new_action_state', false);
      this.diagram_action_mode = false;
      this.new_action_from_id = null;

      // If  new_action_to_state_id is null, then the user is dropping action to global_rect (not to state)
      if (this.new_action_to_state_id != null) {
        const to_state = d3.select(`#d3_rect_${this.new_action_to_state_id}`);
        to_state.classed('d3_new_action_state', false);
        this.handle_create_action(d.id, this.new_action_to_state_id);
        this.new_action_to_state_id = null;
      }
    },

    handle_state_drag(d) {
      d3.select(`#d3_state_g_${d.id}`).attr(
        'transform',
        d => `translate(${[(d.x = d3.event.x), (d.y = d3.event.y)]})`
      );

      // Actions are redrawed each time on drag
      d3.selectAll('.d3_action_g').remove();
      this.redraw_actions();
    },

    handle_radius_changle_drag(d, mouse_position) {
      const source_d = this.ax_states.find(el => el.id == d.from_state_id);
      const target_d = this.ax_states.find(el => el.id == d.to_state_id);
      const source_center = { x: source_d.x, y: source_d.y };
      const target_center = { x: target_d.x, y: target_d.y };
      const mouse = { x: mouse_position[0], y: mouse_position[1] };

      let result_radius = this.get_distance_to_line(
        mouse,
        source_center,
        target_center
      );

      if (result_radius < 10) result_radius = 0;

      if (this.is_left(source_center, target_center, mouse)) {
        result_radius *= -1;
      }

      d.radius = result_radius;
      this.redraw_single_action(d.id);
    },

    redraw_actions() {
      this.d3_actions = this.d3_actions.data(
        this.ax_actions.filter(
          action => action.to_state_id != action.from_state_id
        ),
        d => d.id
      );

      this.d3_actions
        .enter()
        .filter(d => !document.getElementById(`d3_action_g_${d.id}`))
        .append('g')
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_action_g_${d.id}`); // set id for current g
          currentElement.attr('class', 'd3_action_g'); // set class for current g

          currentElement
            .append('path')
            .attr('id', `d3_action_${d.id}`)
            .attr('class', 'd3_line_action')
            .attr('d', this.link_arc_generator)
            .attr('stroke-linecap', 'round')
            .attr('marker-end', (d, i) => 'url(#d3_marker)');
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement
            .append('text')
            .attr('id', `d3_action_text_${d.id}`)
            .attr('class', 'd3_action_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(d => d.name)
            .on('click', d => {
              this.handle_edit_action(d);
            })
            .on('mousedown', d => {
              // event.preventDefault();
              this.state_mouse_down_timestamp = new Date();
              this.change_radius_action_id = d.id;
            })
            .on('mouseover', d => {
              this.selected_action_id = d.id;
            })
            .on('mouseleave', d => {
              this.selected_action_id = null;
            })
            .call(this.drag);
        })
        .merge(this.d3_actions)
        .each(d => {
          // Update function
          const midpoint = this.get_center_of_path(d.id);
          const d3_action_text = d3.select(`#d3_action_text_${d.id}`);
          d3_action_text.attr(
            'transform',
            d => `translate(${[(d.x = midpoint.x), (d.y = midpoint.y)]})`
          );
        });

      this.d3_actions.exit().remove();
    },

    redraw_states() {
      this.d3_states = this.d3_states.data(this.ax_states, d => d.id);

      this.d3_states
        .enter()
        .filter(d => {
          const isNewElement =
            document.getElementById(`d3_rect_${d.id}`) === null && d.type === 1;
          return isNewElement;
        })
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_state')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.id}`); // set id for current g
          currentElement
            .append('rect')
            .attr('id', `d3_rect_${d.id}`)
            .attr('class', 'd3_state_rect')
            .attr('width', this.BOX_WIDTH)
            .attr('height', this.BOX_HEIGHT)
            .attr('rx', this.BOX_RADIUS)
            .attr('ry', this.BOX_RADIUS)
            .attr('x', this.BOX_WIDTH * -0.5)
            .attr('y', 0 - this.BOX_TOP_MARGIN)
            .on('click', d => {
              this.handle_edit_state(d);
            })
            .on('mousedown', d => {
              this.state_mouse_down_timestamp = new Date();
              this.new_action_from_id = d.id;
            })
            .on('mouseover', d => {
              this.selected_state_id = d.id;
              if (this.diagram_action_mode && this.new_action_from_id) {
                const currentRect = d3.select(`#d3_rect_${d.id}`);
                currentRect.classed('d3_new_action_state', true);
                this.new_action_to_state_id = d.id;
              }
            })
            .on('mouseleave', d => {
              this.selected_state_id = null;
              if (this.diagram_action_mode) {
                const currentRect = d3.select(`#d3_rect_${d.id}`);
                currentRect.classed('d3_new_action_state', false);
                this.new_action_to_state_id = null;
              }
            });
        })
        .each((d, i, nodes) => {
          // State text
          const currentElement = d3.select(nodes[i]);
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.id}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(d => d.name)
            .call(this.wrap, this.BOX_WIDTH);
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // Self actions
          let start_height = d3.select(`#d3_rect_${d.id}`)._groups[0][0]
            .attributes.height.value;
          start_height = start_height * 1 + 5; // 5 is first time offset
          const current_state_self_actions = this.ax_actions.filter(
            action =>
              action.to_state_id == action.from_state_id &&
              action.to_state_id == d.id
          );
          current_state_self_actions.forEach(action_d => {
            currentElement
              .append('text')
              .attr('id', `d3_self_action_text_${action_d.id}`)
              .attr('class', 'd3_self_action_text')
              .attr('text-anchor', 'end')
              .attr('alignment-baseline', 'hanging')
              .attr('y', start_height)
              .attr('x', -80)
              .text(() => `→ ${action_d.name}`)
              .on('click', d => {
                this.handle_edit_action(action_d);
              })
              .on('mouseover', d => {
                this.selected_action_id = action_d.id;
              })
              .on('mouseleave', d => {
                this.selected_action_id = null;
              });
            start_height += 20; // incremental_offset
          });
        })
        .merge(this.d3_states);
      // .each((d, i, nodes) => {
      //   const currentElement = d3.select(nodes[i]);
      //   // Update function
      //   let text_height = currentElement
      //     .select('text')
      //     .node()
      //     .getBoundingClientRect().height;
      //   currentElement.select('rect').attr('height', text_height);
      // });

      this.d3_states.exit().remove();
    },

    draw_start() {
      this.d3_start = this.d3_states.data(this.ax_states, d => d.id);

      this.d3_states
        .enter()
        .filter(
          d => !!(!document.getElementById(`d3_rect_${d.id}`) && d.type == 2)
        )
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_start')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.id}`); // set id for current g

          currentElement
            .append('circle')
            .attr('id', 'd3_start')
            .attr('class', 'd3_start')
            .attr('r', 50)
            .on('click', d => {
              handle_edit_state(d);
            })
            .on('mousedown', d => {
              event.preventDefault();
              this.state_mouse_down_timestamp = new Date();
              this.new_action_from_id = d.id;
            });
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // State text
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.id}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(d => d.name);
        })
        .merge(this.d3_states)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // Update function
          // var text_height = currentElement.select('text').node().getBoundingClientRect().height;
          // currentElement.select('rect').attr("height", text_height);
        });

      this.d3_states.exit().remove();
    },

    draw_all() {
      this.d3_start = this.d3_states.data(this.ax_states, d => d.id);

      this.d3_states
        .enter()
        .filter(
          d => !!(!document.getElementById(`d3_rect_${d.id}`) && d.type == 4)
        )
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_all')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.id}`); // set id for current g

          currentElement
            .append('circle')
            .attr('id', 'd3_all')
            .attr('class', 'd3_all')
            .attr('r', 50)
            .on('mousedown', d => {
              event.preventDefault();
              this.state_mouse_down_timestamp = new Date();
              this.new_action_from_id = d.id;
            });
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // State text
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.id}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(d => d.name);
        })
        .merge(this.d3_states)
        .each(d => {});

      this.d3_states.exit().remove();
    },

    draw_end() {
      this.d3_states = this.d3_states.data(this.ax_states, d => d.id);

      this.d3_states
        .enter()
        .filter(
          d => !!(!document.getElementById(`d3_rect_${d.id}`) && d.type == 3)
        )
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_state')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.id}`); // set id for current g
          currentElement
            .append('circle')
            .attr('class', 'd3_end')
            .attr('r', 50);
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement
            .append('circle')
            .attr('class', 'd3_end')
            .attr('r', 45)
            .on('mouseover', d => {
              if (this.diagram_action_mode && this.new_action_from_id) {
                currentElement.classed('d3_new_action_state', true);
                this.new_action_to_state_id = d.id;
              }
            })
            .on('mouseleave', d => {
              if (this.diagram_action_mode) {
                currentElement.classed('d3_new_action_state', false);
                this.new_action_to_state_id = null;
              }
            });
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // State text
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.id}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(d => d.name);
        })
        .merge(this.d3_states);

      this.d3_states.exit().remove();
    },

    redraw_single_action(_id) {
      d3.selectAll(`#d3_action_g_${_id}`).remove();
      this.redraw_actions();
    },

    redraw_single_state(_state_id) {
      d3.selectAll(`#d3_state_g_${_state_id}`).remove();
      this.redraw_states();
    },

    wrap(text, width) {
      const offset = 0;

      text.each((d, i, nodes) => {
        const currentElement = d3.select(nodes[i]);
        const d3_text = d3.select(nodes[i]);
        const words = d3_text
          .text()
          .split(/\s+/)
          .reverse();
        let word;
        let line = [];
        let lineNumber = 0;
        const lineHeight = 0.1;
        const y = d3_text.attr('y');
        const dy = 1;
        let tspan = d3_text
          .text(null)
          .append('tspan')
          .attr('x', offset)
          .attr('y', y)
          .attr('dy', `${dy}em`);
        while ((word = words.pop())) {
          line.push(word);
          tspan.text(line.join(' '));
          if (tspan.node().getComputedTextLength() > width) {
            line.pop();
            tspan.text(line.join(' '));
            line = [word];
            tspan = d3_text
              .append('tspan')
              .attr('x', offset)
              .attr('y', y)
              .attr('dy', `${++lineNumber * lineHeight + dy}em`)
              .text(word);
          }
        }

        // Change rect hight if multiline
        if (lineNumber > 0) {
          const d3_rect = currentElement._groups[0][0].previousElementSibling;
          const new_height = lineNumber * this.WRAP_LINE_HEIGHT;
          d3_rect.setAttribute('height', new_height);
        }
      });
    },

    link_arc_generator(d) {
      const source_d = this.ax_states.find(el => el.id == d.from_state_id);
      const source_obj = document.getElementById(`d3_rect_${d.from_state_id}`);
      const source_center = {
        x: source_d.x,
        y:
          source_d.type == 1
            ? source_d.y + d3.select(source_obj).attr('height') / 2
            : source_d.y,
        h: source_d.type == 1 ? d3.select(source_obj).attr('height') : 50,
        w: source_d.type == 1 ? d3.select(source_obj).attr('width') : 50,
        min_x: null,
        max_x: null,
        min_y: null,
        max_y: null,
        type: source_d.type
      };
      source_center.min_x = source_center.x - source_center.w / 2;
      source_center.max_x = source_center.x + source_center.w / 2;
      source_center.min_y = source_center.y - source_center.h / 2 - 5;
      source_center.max_y = source_center.y + source_center.h / 2 - 5;

      const target_d = this.ax_states.find(el => el.id == d.to_state_id);
      const target_obj = document.getElementById(`d3_rect_${d.to_state_id}`);
      const target_center = {
        x: target_d.x,
        y:
          target_d.type == 1
            ? target_d.y + d3.select(target_obj).attr('height') / 2
            : target_d.y,
        h: target_d.type == 1 ? d3.select(target_obj).attr('height') : 100,
        w: target_d.type == 1 ? d3.select(target_obj).attr('width') : 100,
        min_x: null,
        max_x: null,
        min_y: null,
        max_y: null,
        type: target_d.type
      };
      target_center.min_x = target_center.x - target_center.w / 2;
      target_center.max_x = target_center.x + target_center.w / 2;
      target_center.min_y = target_center.y - target_center.h / 2 - 5;
      target_center.max_y = target_center.y + target_center.h / 2 - 5;

      const sweet_points = this.get_collision_points(
        source_center,
        target_center
      );
      const straight_line = `M${sweet_points.x1},${sweet_points.y1} ${
        sweet_points.x2
      },${sweet_points.y2}`;
      let ret_line = straight_line;

      if (d.radius != 0) {
        const control_point = { x: null, y: null };

        // Находим точку на удалении mouse_distance
        const mouse_distance = d.radius;
        const target_sweet_point = { x: sweet_points.x2, y: sweet_points.y2 };
        const ab05_distance =
          this.get_distance(source_center, target_sweet_point) / 2;
        const r0 = Math.sqrt(
          ab05_distance * ab05_distance + mouse_distance * mouse_distance
        );

        const mouse_distance_points = this.intersect_two_circles(
          source_center.x,
          source_center.y,
          r0,
          target_sweet_point.x,
          target_sweet_point.y,
          r0
        );
        let mouse_distance_point = {};
        if (d.radius > 0) {
          // right or left
          mouse_distance_point = {
            x: mouse_distance_points.x1,
            y: mouse_distance_points.y1
          };
        } else {
          mouse_distance_point = {
            x: mouse_distance_points.x2,
            y: mouse_distance_points.y2
          };
        }

        // P1=2P(0.5)−0.5P0−0.5P2
        // https://math.stackexchange.com/questions/1666026/find-the-control-point-of-quadratic-bezier-curve-having-only-the-end-points
        control_point.x =
          2 * mouse_distance_point.x -
          source_center.x / 2 -
          target_sweet_point.x / 2;
        control_point.y =
          2 * mouse_distance_point.y -
          source_center.y / 2 -
          target_sweet_point.y / 2;

        // draw_debug_circle("debug_control_point", "red", control_point.x, control_point.y);
        // draw_debug_circle("debug_mouse_distance_point", "green", mouse_distance_point.x, mouse_distance_point.y);

        // M50,50 Q50,100 100,100 == Curve from 50,50 to 100,100 with Quadratic Bezier Curve to point 50,100
        const curved_line = `M${source_center.x},${source_center.y}Q${
          control_point.x
        },${control_point.y} ${sweet_points.x2},${sweet_points.y2}`;

        ret_line = curved_line;
      }

      return ret_line;
    },

    /**
     * Finds the intersection point between
     *     * the rectangle
     *       with parallel sides to the x and y axes
     *     * the half-line pointing towards (x,y)
     *       originating from the middle of the rectangle
     *
     * Note: the ,works given min[XY] <= max[XY],
     *       even though minY may not be the "top" of the rectangle
     *       because the coordinate system is flipped.
     * Note: if the input is inside the rectangle,
     *       the line segment wouldn't have an intersection with the rectangle,
     *       but the projected half-line does.
     * Warning: passing in the middle of the rectangle will return the midpoint itself
     *          there are infinitely many half-lines projected in all directions,
     *          so let's just shortcut to midpoint (GIGO).
     *
     * @param x:Number x coordinate of point to build the half-line from
     * @param y:Number y coordinate of point to build the half-line from
     * @param minX:Number the "left" side of the rectangle
     * @param minY:Number the "top" side of the rectangle
     * @param maxX:Number the "right" side of the rectangle
     * @param maxY:Number the "bottom" side of the rectangle
     * @param validate:boolean (optional) whether to treat point inside the rect as error
     * @return an object with x and y members for the intersection
     * @throws if validate == true and (x,y) is inside the rectangle
     * @author TWiStErRob
     * @see <a href="http://stackoverflow.com/a/31254199/253468">source</a>
     * @see <a href="http://stackoverflow.com/a/18292964/253468">based on</a>
     */
    point_on_rect(x, y, minX, minY, maxX, maxY, validate) {
      // assert minX <= maxX;
      // assert minY <= maxY;
      if (validate && (minX < x && x < maxX) && (minY < y && y < maxY)) {
        throw `Point ${[x, y]}cannot be inside ` +
          `the rectangle: ${[minX, minY]} - ${[maxX, maxY]}.`;
      }
      const midX = (minX + maxX) / 2;
      const midY = (minY + maxY) / 2;
      // if (midX - x == 0) -> m == ±Inf -> minYx/maxYx == x (because value / ±Inf = ±0)
      const m = (midY - y) / (midX - x);

      if (x <= midX) {
        // check "left" side
        const minXy = m * (minX - x) + y;
        if (minY <= minXy && minXy <= maxY) return { x: minX, y: minXy };
      }

      if (x >= midX) {
        // check "right" side
        const maxXy = m * (maxX - x) + y;
        if (minY <= maxXy && maxXy <= maxY) return { x: maxX, y: maxXy };
      }

      if (y <= midY) {
        // check "top" side
        const minYx = (minY - y) / m + x;
        if (minX <= minYx && minYx <= maxX) return { x: minYx, y: minY };
      }

      if (y >= midY) {
        // check "bottom" side
        const maxYx = (maxY - y) / m + x;
        if (minX <= maxYx && maxYx <= maxX) return { x: maxYx, y: maxY };
      }

      // edge case when finding midpoint intersection: m = 0/0 = NaN
      if (x === midX && y === midY) console.log('ERROR');

      // Should never happen :) If it does, please tell me!
      throw `Cannot find intersection for ${[x, y]} inside rectangle ${[
        minX,
        minY
      ]} - ${[maxX, maxY]}.`;
    },

    get_collision_points(source, target, nodeSize) {
      let sourceX;
      let targetX;
      let midX;
      let dx;
      let dy;
      let angle;

      // This mess makes the arrows exactly perfect.
      if (source.max_x < target.min_x) {
        sourceX = source.max_x;
        targetX = target.min_x;
      } else if (target.max_x < source.min_x) {
        targetX = target.max_x;
        sourceX = source.min_x;
      } else {
        midX = (source.x + target.x) / 2;
        if (midX > target.max_x) {
          midX = target.max_x;
        } else if (midX > source.max_x) {
          midX = source.max_x;
        } else if (midX < target.min_x) {
          midX = target.min_x;
        } else if (midX < source.min_x) {
          midX = source.min_x;
        }
        targetX = sourceX = midX;
      }

      dx = targetX - sourceX;
      dy = target.y - source.y;
      angle = Math.atan2(dx, dy);

      return {
        x1: sourceX,
        y1: source.y + (Math.cos(angle) * source.h) / 2,
        x2: targetX,
        y2: target.y - (Math.cos(angle) * target.h) / 2
      };
    },

    handle_create_state() {
      const global_g = document.getElementById('global_g');
      const coords = d3.mouse(global_g);

      const oldest_state = this.ax_states.reduce((prev, current) =>
        prev.id > current.id ? prev : current
      );

      const new_state = {
        id: oldest_state.id + 1,
        x: coords[0],
        y: coords[1],
        name: 'New State',
        type: 1
      };
      this.ax_states.push(new_state);
      this.redraw_states();
    },

    handle_create_action(_from_state_id, _to_state_id) {
      const oldest_action = this.ax_actions.reduce((prev, current) =>
        prev.id > current.id ? prev : current
      );
      const new_action_id = oldest_action.id + 1;

      const new_action = {
        id: new_action_id,
        from_state_id: _from_state_id,
        to_state_id: _to_state_id,
        name: `New action ${new_action_id}`,
        radius: 0
      };

      this.ax_actions.push(new_action);

      if (_from_state_id == _to_state_id) {
        this.redraw_single_state(_from_state_id);
      } else this.redraw_actions();

      console.log(`CREATE ACTION FROM ${_from_state_id} TO ${_to_state_id}`);
    },

    handle_edit_state(d) {
      console.log(`HANDLE EDIT STATE ${d.id}`);
    },

    handle_edit_action(d) {
      console.log(`HANDLE EDIT ACTION ${d.id}`);
    },

    handle_state_delete(_id) {
      console.log(`DELETE STATE ${_id}`);
    },

    handle_action_delete(_id) {
      console.log(`DELETE ACTION ${_id}`);
    },

    intersect_two_circles(x1, y1, r1, x2, y2, r2) {
      const centerdx = x1 - x2;
      const centerdy = y1 - y2;
      const R = Math.sqrt(centerdx * centerdx + centerdy * centerdy);
      if (!(Math.abs(r1 - r2) <= R && R <= r1 + r2)) {
        // no intersection
        return null; // empty list of results
      }
      // intersection(s) should exist

      const R2 = R * R;
      const R4 = R2 * R2;
      const a = (r1 * r1 - r2 * r2) / (2 * R2);
      const r2r2 = r1 * r1 - r2 * r2;
      const c = Math.sqrt(
        (2 * (r1 * r1 + r2 * r2)) / R2 - (r2r2 * r2r2) / R4 - 1
      );

      const fx = (x1 + x2) / 2 + a * (x2 - x1);
      const gx = (c * (y2 - y1)) / 2;
      const ix1 = fx + gx;
      const ix2 = fx - gx;

      const fy = (y1 + y2) / 2 + a * (y2 - y1);
      const gy = (c * (x1 - x2)) / 2;
      const iy1 = fy + gy;
      const iy2 = fy - gy;

      // note if gy == 0 and gx == 0 then the circles are tangent and there is only one solution
      // but that one solution will just be duplicated as the code is currently written
      // return [
      //     [ix1, iy1],
      //     [ix2, iy2]
      // ];
      return {
        x1: ix1,
        y1: iy1,
        x2: ix2,
        y2: iy2
      };
    },

    is_left(_line_from, _line_to, _point) {
      // if value > 0, p2 is on the left side of the line.
      // if value = 0, p2 is on the same line.
      // if value < 0, p2 is on the right side of the line.
      const value =
        (_line_to.x - _line_from.x) * (_point.y - _line_from.y) -
        (_point.x - _line_from.x) * (_line_to.y - _line_from.y);
      if (value > 0) return true;
      return false;
    },

    get_distance(a, b) {
      const side_a = a.x - b.x;
      const side_b = a.y - b.y;
      return Math.sqrt(side_a * side_a + side_b * side_b);
    },

    get_distance_squared(v, w) {
      return (v.x - w.x) * (v.x - w.x) + (v.y - w.y) * (v.y - w.y);
    },

    get_center_of_path(_id) {
      const pathEl = d3.select(`#d3_action_${_id}`).node();
      const midpoint = pathEl.getPointAtLength(pathEl.getTotalLength() / 2);
      return midpoint;
    },

    get_distance_to_line(_point, _line_start, _line_end) {
      const l2 = this.get_distance_squared(_line_start, _line_end);

      if (l2 == 0) {
        return Math.sqrt(this.get_distance_squared(_point, _line_start));
      }

      const t =
        ((_point.x - _line_start.x) * (_line_end.x - _line_start.x) +
          (_point.y - _line_start.y) * (_line_end.y - _line_start.y)) /
        l2;
      if (t < 0) {
        return Math.sqrt(this.get_distance_squared(_point, _line_start));
      }
      if (t > 1) return Math.sqrt(this.get_distance_squared(_point, _line_end));

      const distance_squared = this.get_distance_squared(_point, {
        x: _line_start.x + t * (_line_end.x - _line_start.x),
        y: _line_start.y + t * (_line_end.y - _line_start.y)
      });
      return Math.sqrt(distance_squared);
    },

    draw_debug_circle(_id, _color, _x, _y) {
      d3.selectAll(`#${_id}`).remove();

      const circle = this.container
        .append('circle')
        .attr('id', _id)
        .attr('cx', _x)
        .attr('cy', _y)
        .attr('r', 5)
        .style('fill', _color);
    },

    check_delete(event) {
      if (event.keyCode == 46) {
        if (this.selected_state_id != null) {
          this.handle_state_delete(this.selected_state_id);
        }

        if (this.selected_action_id != null) {
          this.handle_action_delete(this.selected_action_id);
        }
      }
    }
  }
};
</script>

<style scoped>
.footer {
  position: absolute;
  right: 10px;
  bottom: 10px;
}
</style>
