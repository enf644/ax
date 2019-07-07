<template>
  <div id='workflowContainer' ref='workflowContainer'>
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
    <resize-observer @notify='debounceResize' />

    <modal adaptive height='auto' name='update-state' scrollable width='1000px'>
      <TheStateModal
        :guid='this.selectedStateGuid'
        @close='closeModal'
        @updateState='updateModalState'
        ref='stateModal'
      />
    </modal>

    <modal adaptive height='auto' name='update-action' scrollable width='1000px'>
      <TheActionModal
        :guid='this.selectedActionGuid'
        @close='closeModal'
        @updateAction='updateModalAction'
        ref='actionModal'
      />
    </modal>
  </div>
</template>

<script>
import * as d3 from 'd3';
import { debounce } from '@/misc';
import TheStateModal from '@/components/ConstructorWorkflow/TheStateModal.vue';
import TheActionModal from '@/components/ConstructorWorkflow/TheActionModal.vue';

export default {
  name: 'WorkflowConstructorContent',
  components: { TheStateModal, TheActionModal },
  data: () => ({
    selectedStateGuid: null,
    selectedActionGuid: null,
    resizeWidth: null,
    resizeHeight: null,
    containerMargin: null,
    containerWidth: null,
    containerHeight: null,
    BOX_WIDTH: 200,
    BOX_HEIGHT: 40,
    BOX_TOP_MARGIN: 0,
    BOX_RADIUS: 20,
    WRAP_LINE_HEIGHT: 35,
    NEW_ACTION_TIMEOUT: 150,
    stateMouseDownTimestamp: null,
    actionMousedownPosition: null,
    diagramActionMode: false,
    newActionFromId: null,
    newActiontoStateGuid: null,
    changeRadiusActionId: null,
    change_starting_radius: null,
    selectedStateId: null,
    selectedActionId: null,
    dragStartPosition: {},
    zoom: null,
    drag: null,
    svg: null,
    globalG: null,
    globalRect: null,
    container: null,
    d3Actions: null,
    d3States: null,
    newActionLine: null,
    d3Initialized: false,
    emInPx: null
  }),
  computed: {
    hightlightedRole() {
      return this.$store.state.workflow.highlightedRole;
    },
    defaultGridDbName() {
      const defaultGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      return defaultGrid ? defaultGrid.dbName : null;
    },
    debounceResize() {
      return debounce(this.handleResize, 2000);
    },
    axStates() {
      return this.$store.state.workflow.states;
    },
    axActions() {
      return this.$store.state.workflow.actions;
    },
    addedAction() {
      return this.$store.state.workflow.addedAction;
    }
  },
  watch: {
    hightlightedRole(newValue) {
      if (newValue) {
        const states2lite = [];
        this.$store.state.workflow.states.forEach(state => {
          state.roles.edges.forEach(edge => {
            if (edge.node.guid === newValue.guid) states2lite.push(state);
          });
        });

        states2lite.forEach(state => {
          if (state.isStart) {
            const startState = d3.select('#d3_start');
            startState.style('fill', newValue.color);
            startState.classed('d3_highlighted_state', true);
          } else {
            const currentState = d3.select(`#d3_rect_${state.guid}`);
            currentState.style('fill', newValue.color);
            currentState.classed('d3_highlighted_state', true);
          }
        });

        const actions2lite = [];
        this.$store.state.workflow.actions.forEach(action => {
          action.roles.edges.forEach(edge => {
            if (edge.node.guid === newValue.guid) actions2lite.push(action);
          });
        });

        actions2lite.forEach(action => {
          const currentAction = d3.select(`#d3_action_${action.guid}`);
          currentAction.style('stroke', newValue.color);
          currentAction.classed('d3_highlighted_action', true);

          const currentArrow = d3.select(`#d3_marker_${action.guid}`);
          currentArrow.style('stroke', newValue.color);
          currentArrow.style('fill', newValue.color);
          currentArrow.classed('d3_highlighted_action', true);
        });
      } else {
        this.axStates.forEach(state => {
          const currentState = d3.select(`#d3_rect_${state.guid}`);
          currentState.style('fill', null);
          currentState.classed('d3_highlighted_state', false);
        });

        this.axActions.forEach(action => {
          const currentAction = d3.select(`#d3_action_${action.guid}`);
          currentAction.style('stroke', null);
          currentAction.classed('d3_highlighted_action', false);

          const currentArrow = d3.select(`#d3_marker_${action.guid}`);
          currentArrow.style('stroke', null);
          currentArrow.style('fill', null);
          currentArrow.classed('d3_highlighted_action', false);
        });

        const startState = d3.select('#d3_start');
        startState.style('fill', null);
        startState.classed('d3_highlighted_state', false);
      }
    },
    axStates(newValue, oldValue) {
      if (newValue && oldValue.length === 0) this.initD3();
      if (newValue && this.d3Initialized) this.redrawStates();
    },
    axActions(newValue) {
      if (newValue && this.d3Initialized) {
        this.redrawActions();
      }
    },
    addedAction(newValue) {
      if (newValue && newValue) {
        if (newValue.fromStateGuid === newValue.toStateGuid) {
          this.redrawSingleState(newValue.fromStateGuid);
        }
      }
    }
  },
  mounted() {
    if (!this.d3Initialized && this.axStates.length > 0) this.initD3();
    // get height in px of 1em
    this.emInPx = Number(
      window
        .getComputedStyle(document.body)
        .getPropertyValue('font-size')
        .match(/\d+/)[0]
    );
  },
  methods: {
    initD3() {
      this.initData();
      this.initZoom();
      this.initDrag();
      this.initSvg();

      this.redrawStates();
      this.drawStart();
      this.drawEnd();
      this.drawAll();
      this.redrawActions();

      this.d3Initialized = true;
    },
    handleResize() {
      const deltaX = Math.abs(
        this.resizeWidth - this.$refs.workflowContainer.clientWidth
      );
      const deltaY = Math.abs(
        this.resizeHeight - this.$refs.workflowContainer.clientHeight
      );

      if (this.d3Initialized && (deltaX > 10 || deltaY > 10)) {
        d3.select('svg').remove();
        setTimeout(() => {
          this.initD3();
        }, 1000);
      }
    },

    initData() {
      window.addEventListener('keyup', this.checkDelete);

      this.containerMargin = {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      };
      const paneWidth = this.$refs.workflowContainer.clientWidth;
      const paneHeight = this.$refs.workflowContainer.clientHeight;
      this.resizeWidth = this.$refs.workflowContainer.clientWidth;
      this.resizeHeight = this.$refs.workflowContainer.clientHeight;
      const { left } = this.containerMargin;
      const { right } = this.containerMargin;
      const { top } = this.containerMargin;
      const { bottom } = this.containerMargin;
      this.containerWidth = paneWidth - left - right - 10;
      this.containerHeight = paneHeight - top - bottom - 10;
    },
    initZoom() {
      this.zoom = d3
        .zoom()
        .scaleExtent([0.2, 1])
        .on('zoom', () => {
          const globalG = d3.select(document.getElementById('globalG'));
          globalG.attr('transform', d3.event.transform);
        });
    },
    initDrag() {
      this.drag = d3
        .drag()
        .subject(d => d)
        .on('start', () => {
          d3.event.sourceEvent.stopPropagation();
          this.dragStartPosition.x = d3.event.x;
          this.dragStartPosition.y = d3.event.y;
        })
        .on('drag', (d, i, nodes) => {
          let elementIsDragged = false;
          const { x } = this.dragStartPosition;
          const { y } = this.dragStartPosition;
          if (d3.event.x !== x || d3.event.y !== y) elementIsDragged = true;

          // If user is holding mouse for some time - it is action mode
          // (create action or change radius)
          const timeDelta = new Date() - this.stateMouseDownTimestamp;
          this.diagramActionMode = !(
            this.stateMouseDownTimestamp != null
            && timeDelta < this.NEW_ACTION_TIMEOUT
          );
          if (elementIsDragged) this.stateMouseDownTimestamp = null;

          if (this.diagramActionMode && this.newActionFromId) {
            const currentState = nodes[i];
            const mousePosition = d3.mouse(currentState);
            this.handleNewActionDrag(d, mousePosition);
          } else if (this.diagramActionMode && this.changeRadiusActionId) {
            const globalG = document.getElementById('globalG');
            const mousePosition = d3.mouse(globalG);
            this.handleRadiusChangleDrag(d, mousePosition);
          } else if (elementIsDragged) {
            this.diagramActionMode = false;
            this.newActionFromId = null;
            this.handleStateDrag(d);
          }
        })
        .on('end', d => {
          if (this.diagramActionMode && this.newActionFromId) {
            this.handleNewActionDragend(d);
          } else if (this.diagramActionMode && this.changeRadiusActionId) {
            this.diagramActionMode = false;
            this.changeRadiusActionId = null;
            this.actionMousedownPosition = null;
            this.dispatchActionChange(d);
          } else {
            this.diagramActionMode = false;
            this.dispatchStateChange(d);
            this.redrawStates();
          }
        });
    },
    initSvg() {
      const initialX = this.containerWidth / 2;
      const initialY = this.containerHeight / 2;
      const initialZoom = 1; // 0.75

      this.svg = d3
        .select('#d3div')
        .append('svg')
        .attr(
          'width',
          this.containerWidth
            + this.containerMargin.left
            + this.containerMargin.right
        )
        .attr(
          'height',
          this.containerHeight
            + this.containerMargin.top
            + this.containerMargin.bottom
        )
        .append('g')
        .attr(
          'transform',
          `translate(${this.containerMargin.left},${this.containerMargin.right})`
        )
        .call(this.zoom)
        .call(
          this.zoom.transform,
          d3.zoomIdentity.translate(initialX, initialY).scale(initialZoom)
        );

      // Declare actions arrow marker
      // this.svg
      //   .append('defs')
      //   .selectAll('marker')
      //   .data(this.axActions)
      //   .enter()
      //   .append('marker')
      //   .attr('id', data => {
      //     return `d3_marker_${data.guid}`;
      //   })
      //   .attr('class', () => 'd3_marker')
      //   .attr('viewBox', '0 -5 10 10')
      //   .attr('refX', 10)
      //   .attr('markerWidth', 10)
      //   .attr('markerHeight', 10)
      //   .attr('orient', 'auto')
      //   .append('svg:path')
      //   .attr('d', 'M0,-5L10,0L0,5')
      //   .attr('class', 'end-arrow');

      // declare  new action marker
      this.svg
        .append('defs')
        .selectAll('marker')
        .data(this.axActions)
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
      this.globalRect = this.svg
        .append('rect')
        .attr('width', this.containerWidth)
        .attr('height', this.containerHeight)
        .style('fill', 'none')
        .style('pointer-events', 'all')
        .attr('id', 'globalRect')
        .on('dblclick', this.handleCreateState)
        .on('mousemove', () => {});

      // Decalre container g - it holds all states and actions
      this.container = this.svg
        .append('g')
        .attr('id', 'globalG')
        .attr(
          'transform',
          () => `translate(${initialX},${initialY}) scale(${initialZoom},${initialZoom})`
        )
        .on('mousemove', () => {});

      //  Declare actions array and bind it to ax_actions data
      this.d3Actions = this.container
        .append('g')
        .selectAll('g.d3_action_g')
        .data(
          this.axActions.filter(
            action => action.toStateGuid !== action.fromStateGuid
          )
        );

      //  Declare states array and bind it to axStates data
      this.d3States = this.container
        .append('g')
        .selectAll('g.g_state')
        .data(this.axStates);

      // New action line - is vissible only on action creation
      this.newActionLine = this.container
        .append('line')
        .attr('class', 'd3_new_action hidden')
        .attr('id', 'd3_new_action')
        .attr('marker-end', () => 'url(#d3_new_action_marker)')
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', 0)
        .attr('y2', 0);

      this.svg.on('dblclick.zoom', null); // Disable double click for zoom
    },

    handleNewActionDrag(d, mousePosition) {
      const stateX = d.x;
      const stateY = d.y;
      const actionLine = d3.select('#d3_new_action');
      actionLine
        .classed('hidden', false)
        .attr('x1', stateX)
        .attr('y1', stateY + this.BOX_HEIGHT / 2)
        .attr('x2', stateX + mousePosition[0])
        .attr('y2', stateY + mousePosition[1]);

      const currentState = d3.select(`#d3_rect_${d.guid}`);
      currentState.classed('d3_new_action_state', true);
    },

    handleNewActionDragend(d) {
      const actionLine = d3.select('#d3_new_action');
      actionLine.classed('hidden', true);
      const fromState = d3.select(`#d3_rect_${d.guid}`);
      fromState.classed('d3_new_action_state', false);
      const endState = d3.select('#d3_end');
      endState.classed('d3_new_action_state', false);

      this.diagramActionMode = false;
      this.newActionFromId = null;

      // If  newActiontoStateGuid is null, then the user is dropping action to globalRect
      // (not to state)
      if (this.newActiontoStateGuid != null) {
        const toState = d3.select(`#d3_rect_${this.newActiontoStateGuid}`);
        toState.classed('d3_new_action_state', false);
        this.handleCreateAction(d.guid, this.newActiontoStateGuid);
        this.newActiontoStateGuid = null;
      }
    },

    dispatchStateChange(data) {
      const newState = {
        guid: data.guid,
        x: data.x,
        y: data.y
      };
      this.$store
        .dispatch('workflow/updateStatePosition', newState)
        .then(() => {});
    },

    setStateData(data) {
      const newState = {
        guid: data.guid,
        x: data.x,
        y: data.y
      };
      this.$store.commit('workflow/setStatePosition', newState);
    },

    setActionData(data) {
      // const index = this.axActions.findIndex(
      //   action => action.guid === data.guid
      // );
      // if (data.radius) this.axActions[index].radius = data.radius;

      const newAction = {
        guid: data.guid,
        radius: data.radius
      };
      this.$store.commit('workflow/updateActionRadius', newAction);
    },

    dispatchActionChange(data) {
      const newAction = {
        guid: data.guid,
        radius: data.radius
      };
      this.$store.dispatch('workflow/updateActionRadius', newAction);
    },

    handleStateDrag(d) {
      d3.select(`#d3_state_g_${d.guid}`).attr('transform', data => {
        const newStateData = {
          guid: data.guid,
          x: d3.event.x,
          y: d3.event.y
        };
        this.setStateData(newStateData);
        return `translate(${[d3.event.x, d3.event.y]})`;
      });

      // Actions are redrawed each time on drag
      // d3.selectAll('.d3_action_g').remove();
      const formActions = this.$store.state.workflow.actions.filter(
        action => action.fromStateGuid === d.guid
      );
      formActions.forEach(element => {
        d3.select(`#d3_action_g_${element.guid}`).remove();
      });
      const toActions = this.$store.state.workflow.actions.filter(
        action => action.toStateGuid === d.guid
      );
      toActions.forEach(element => {
        d3.select(`#d3_action_g_${element.guid}`).remove();
      });
      this.redrawActions();
    },

    handleRadiusChangleDrag(d, mousePosition) {
      const sourceD = this.axStates.find(el => el.guid === d.fromStateGuid);
      const targetD = this.axStates.find(el => el.guid === d.toStateGuid);
      const sourceCenter = { x: sourceD.x, y: sourceD.y };
      const targetCenter = { x: targetD.x, y: targetD.y };
      const mouse = { x: mousePosition[0], y: mousePosition[1] };

      let resultRadius = this.getDistanceToLine(
        mouse,
        sourceCenter,
        targetCenter
      );

      if (resultRadius < 10) resultRadius = 0;

      if (this.isLeft(sourceCenter, targetCenter, mouse)) {
        resultRadius *= -1;
      }

      // d.radius = resultRadius;
      this.setActionData({
        guid: d.guid,
        radius: resultRadius
      });

      this.redrawSingleAction(d.guid);
    },

    redrawActions() {
      this.d3Actions = this.d3Actions.data(
        this.axActions.filter(
          action => action.toStateGuid !== action.fromStateGuid
        ),
        d => d.guid
      );

      this.d3Actions
        .enter()
        .filter(d => {
          const element = document.getElementById(`d3_action_g_${d.guid}`);
          const isNewElement = element === null;
          return isNewElement;
        })
        .append('g')
        .each(data => {
          this.svg
            .append('defs')
            .append('marker')
            .attr('id', `d3_marker_${data.guid}`)
            .attr('class', () => 'd3_marker')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 10)
            .attr('markerWidth', 10)
            .attr('markerHeight', 10)
            .attr('orient', 'auto')
            .append('svg:path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('class', 'end-arrow');
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_action_g_${d.guid}`); // set id for current g
          currentElement.attr('class', 'd3_action_g'); // set class for current g

          currentElement
            .append('path')
            .attr('id', `d3_action_${d.guid}`)
            .attr('class', 'd3_line_action')
            .attr('d', this.linkArcGenerator)
            .attr('stroke-linecap', 'round')
            .attr('marker-end', () => `url(#d3_marker_${d.guid})`);
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement
            .append('text')
            .attr('id', `d3_action_text_${d.guid}`)
            .attr('class', 'd3_action_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(data => data.name)
            .on('click', data => {
              this.handleEditAction(data);
            })
            .on('mousedown', data => {
              // event.preventDefault();
              this.stateMouseDownTimestamp = new Date();
              this.changeRadiusActionId = data.guid;
            })
            .on('mouseover', data => {
              this.selectedActionId = data.guid;
            })
            .on('mouseleave', () => {
              this.selectedActionId = null;
            })
            .on('dragover', data => {
              // Allow drop
              d3.event.preventDefault();
              const currentLine = d3.select(`#d3_action_${data.guid}`);
              currentLine.classed('d3_dragover_line', true);

              const currentArrow = d3.select(`#d3_marker_${data.guid}`);
              currentArrow.classed('d3_dragover_line_arrow', true);
            })
            .on('dragleave', data => {
              const currentLine = d3.select(`#d3_action_${data.guid}`);
              currentLine.classed('d3_dragover_line', false);

              const currentArrow = d3.select(`#d3_marker_${data.guid}`);
              currentArrow.classed('d3_dragover_line_arrow', false);
            })
            .on('drop', data => {
              const currentLine = d3.select(`#d3_action_${data.guid}`);
              currentLine.classed('d3_dragover_line', false);

              const currentArrow = d3.select(`#d3_marker_${data.guid}`);
              currentArrow.classed('d3_dragover_line_arrow', false);

              const roleGuid = d3.event.dataTransfer.getData('roleGuid');
              this.handleAddRoleToAction(roleGuid, data.guid);
            })
            .call(this.drag);
        })
        .merge(this.d3Actions)
        .each(d => {
          // Update function
          const midpoint = this.getCenterOfPath(d.guid);
          const d3ActionText = d3.select(`#d3_action_text_${d.guid}`);
          d3ActionText.attr(
            'transform',
            () => `translate(${[midpoint.x, midpoint.y]})`
          );
        });

      this.d3Actions.exit().remove();
    },

    redrawStates() {
      this.d3States = this.d3States.data(this.axStates, d => d.guid);
      this.d3States
        .enter()
        .filter(d => {
          const element = document.getElementById(`d3_rect_${d.guid}`);
          // prettier-ignore
          const isNewElement = element === null
            && (d.isStart === false && d.isDeleted === false && d.isAll === false);
          return isNewElement;
        })
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_state')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.guid}`); // set id for current g
          currentElement
            .append('rect')
            .attr('id', `d3_rect_${d.guid}`)
            .attr('class', 'd3_state_rect')
            .attr('width', this.BOX_WIDTH)
            .attr('height', this.BOX_HEIGHT)
            .attr('rx', this.BOX_RADIUS)
            .attr('ry', this.BOX_RADIUS)
            .attr('x', this.BOX_WIDTH * -0.5)
            .attr('y', 0 - this.BOX_TOP_MARGIN)
            .on('click', data => {
              this.handleEditState(data);
            })
            .on('mousedown', data => {
              this.stateMouseDownTimestamp = new Date();
              this.newActionFromId = data.guid;
            })
            .on('mouseover', data => {
              this.selectedStateId = data.guid;
              if (this.diagramActionMode && this.newActionFromId) {
                const currentRect = d3.select(`#d3_rect_${data.guid}`);
                currentRect.classed('d3_new_action_state', true);
                this.newActiontoStateGuid = data.guid;
              }
            })
            .on('mouseleave', data => {
              this.selectedStateId = null;
              if (this.diagramActionMode) {
                const currentRect = d3.select(`#d3_rect_${data.guid}`);
                currentRect.classed('d3_new_action_state', false);
                this.newActiontoStateGuid = null;
              }
            })
            .on('dragover', data => {
              // Allow drop
              d3.event.preventDefault();
              const currentRect = d3.select(`#d3_rect_${data.guid}`);
              currentRect.classed('d3_dragover', true);
            })
            .on('dragleave', data => {
              const currentRect = d3.select(`#d3_rect_${data.guid}`);
              currentRect.classed('d3_dragover', false);
            })
            .on('drop', data => {
              const currentRect = d3.select(`#d3_rect_${data.guid}`);
              currentRect.classed('d3_dragover', false);

              const roleGuid = d3.event.dataTransfer.getData('roleGuid');
              this.handleAddRoleToState(roleGuid, data.guid);
            });
        })
        .each((d, i, nodes) => {
          // State text
          const currentElement = d3.select(nodes[i]);
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.guid}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            // .attr('y', 7)
            .attr('alignment-baseline', 'alphabetic')
            .text(data => data.name)
            .call(this.wrap, this.BOX_WIDTH);
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // Self actions
          // eslint-disable-next-line no-underscore-dangle
          let startHeight = d3.select(`#d3_rect_${d.guid}`)._groups[0][0]
            .attributes.height.value;
          startHeight = startHeight * 1 + 5; // 5 is first time offset
          const currentStateSelfActions = this.axActions.filter(
            action => action.toStateGuid === action.fromStateGuid
              && action.toStateGuid === d.guid
          );
          currentStateSelfActions.forEach(actionD => {
            currentElement
              .append('text')
              .attr('id', `d3_self_action_text_${actionD.guid}`)
              .attr('class', 'd3_self_action_text')
              .attr('text-anchor', 'end')
              .attr('alignment-baseline', 'hanging')
              .attr('y', startHeight)
              .attr('x', -80)
              .text(() => `→ ${actionD.name}`)
              .on('click', () => {
                this.handleEditAction(actionD);
              })
              .on('mouseover', () => {
                this.selectedActionId = actionD.guid;
              })
              .on('mouseleave', () => {
                this.selectedActionId = null;
              });
            startHeight += 20; // incremental_offset
          });
        })
        .merge(this.d3States);
      // .each((d, i, nodes) => {
      //   const currentElement = d3.select(nodes[i]);
      //   // Update function
      //   let text_height = currentElement
      //     .select('text')
      //     .node()
      //     .getBoundingClientRect().height;
      //   currentElement.select('rect').attr('height', text_height);
      // });

      this.d3States.exit().remove();
    },

    drawStart() {
      this.d3_start = this.d3States.data(this.axStates, d => d.guid);

      this.d3States
        .enter()
        .filter(
          // prettier-ignore
          d => !!(
            !document.getElementById(`d3_rect_${d.guid}`)
              && d.isStart === true
          )
        )
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_start')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.guid}`); // set id for current g

          currentElement
            .append('circle')
            .attr('id', 'd3_start')
            .attr('class', 'd3_start')
            .attr('r', 50)
            .on('click', data => {
              this.handleEditState(data);
            })
            .on('mousedown', data => {
              // event.preventDefault();
              this.stateMouseDownTimestamp = new Date();
              this.newActionFromId = data.guid;
            })
            .on('dragover', () => {
              // Allow drop
              d3.event.preventDefault();
              const currentRect = d3.select('#d3_start');
              currentRect.classed('d3_dragover', true);
            })
            .on('dragleave', () => {
              const currentRect = d3.select('#d3_start');
              currentRect.classed('d3_dragover', false);
            })
            .on('drop', data => {
              const currentRect = d3.select('#d3_start');
              currentRect.classed('d3_dragover', false);

              const roleGuid = d3.event.dataTransfer.getData('roleGuid');
              this.handleAddRoleToState(roleGuid, data.guid);
            });
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // State text
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.guid}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(data => data.name);
        })
        .merge(this.d3States);
      // .each((d, i, nodes) => {
      // const currentElement = d3.select(nodes[i]);
      // Update function
      // var text_height = currentElement.select('text').node().getBoundingClientRect().height;
      // currentElement.select('rect').attr("height", text_height);
      // });

      this.d3States.exit().remove();
    },

    drawAll() {
      this.d3_start = this.d3States.data(this.axStates, d => d.guid);

      this.d3States
        .enter()
        .filter(
          // prettier-ignore
          d => !!(
            !document.getElementById(`d3_rect_${d.guid}`) && d.isAll === true
          )
        )
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_all')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.guid}`); // set id for current g

          currentElement
            .append('circle')
            .attr('id', 'd3_all')
            .attr('class', 'd3_all')
            .attr('r', 50)
            .on('mousedown', data => {
              // event.preventDefault();
              this.stateMouseDownTimestamp = new Date();
              this.newActionFromId = data.guid;
            });
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // State text
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.guid}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(data => data.name);
        })
        .merge(this.d3States);

      this.d3States.exit().remove();
    },

    drawEnd() {
      this.d3States = this.d3States.data(this.axStates, d => d.guid);

      this.d3States
        .enter()
        .filter(
          // prettier-ignore
          d => !!(
            !document.getElementById(`d3_rect_${d.guid}`)
              && d.isDeleted === true
          )
        )
        .append('g')
        .attr('transform', d => `translate(${[d.x, d.y]})`) // starting position of state group
        .attr('class', 'g_end')
        .call(this.drag)
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement.attr('id', `d3_state_g_${d.guid}`); // set id for current g
          currentElement
            .append('circle')
            .attr('class', 'd3_end')
            .attr('r', 50);
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          currentElement
            .append('circle')
            .attr('id', 'd3_end')
            .attr('class', 'd3_end')
            .attr('r', 45)
            .on('mouseover', data => {
              if (this.diagramActionMode && this.newActionFromId) {
                const currentRect = d3.select('#d3_end');
                currentRect.classed('d3_new_action_state', true);
                this.newActiontoStateGuid = data.guid;
              }
            })
            .on('mouseleave', () => {
              if (this.diagramActionMode) {
                const currentRect = d3.select('#d3_end');
                currentRect.classed('d3_new_action_state', false);
                this.newActiontoStateGuid = null;
              }
            });
        })
        .each((d, i, nodes) => {
          const currentElement = d3.select(nodes[i]);
          // State text
          currentElement
            .append('text')
            .attr('id', `d3_text_${d.guid}`)
            .attr('class', 'd3_state_text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'alphabetic')
            .text(data => data.name);
        })
        .merge(this.d3States);

      this.d3States.exit().remove();
    },

    redrawSingleAction(_id) {
      d3.selectAll(`#d3_action_g_${_id}`).remove();
      this.redrawActions();
    },

    redrawSingleState(stateId) {
      d3.selectAll(`#d3_state_g_${stateId}`).remove();
      this.redrawStates();
    },

    wrap(text, width) {
      const offset = 0;

      text.each((d, i, nodes) => {
        const currentElement = d3.select(nodes[i]);
        const d3Text = d3.select(nodes[i]);
        const words = d3Text
          .text()
          .split(/\s+/)
          .reverse();
        let word;
        let line = [];
        let lineNumber = 0;
        const lineHeight = 0.1;
        const y = d3Text.attr('y');
        const dy = 1.3;
        let tspan = d3Text
          .text(null)
          .append('tspan')
          .attr('x', offset)
          .attr('y', y)
          .attr('dy', `${dy}em`);
        while (words.length > 0) {
          word = words.pop();
          line.push(word);
          tspan.text(line.join(' '));
          if (tspan.node().getComputedTextLength() > width) {
            line.pop();
            tspan.text(line.join(' '));
            line = [word];
            lineNumber += 1;
            tspan = d3Text
              .append('tspan')
              .attr('x', offset)
              .attr('y', y)
              .attr('dy', `${lineNumber * lineHeight + dy}em`)
              .text(word);
          }
        }

        // Change rect hight if multiline
        if (lineNumber > 0) {
          // eslint-disable-next-line no-underscore-dangle
          const d3Rect = currentElement._groups[0][0].previousElementSibling;
          // const newHeight = lineNumber * this.WRAP_LINE_HEIGHT + 10;
          const newHeight = currentElement.node().getBoundingClientRect()
            .height;
          d3Rect.setAttribute('height', newHeight + 10);
        }
      });
    },

    linkArcGenerator(d) {
      const sourceD = this.axStates.find(el => el.guid === d.fromStateGuid);
      const sourceObj = document.getElementById(`d3_rect_${d.fromStateGuid}`);
      // prettier-ignore
      const sourceIsState = sourceD.isStart === false
        && sourceD.isDeleted === false
        && sourceD.isAll === false;
      const sourceCenter = {
        x: sourceD.x,
        y: sourceIsState
          ? sourceD.y + d3.select(sourceObj).attr('height') / 2
          : sourceD.y,
        h: sourceIsState ? d3.select(sourceObj).attr('height') : 50,
        w: sourceIsState ? d3.select(sourceObj).attr('width') : 50,
        min_x: null,
        max_x: null,
        min_y: null,
        max_y: null
      };
      sourceCenter.min_x = sourceCenter.x - sourceCenter.w / 2;
      sourceCenter.max_x = sourceCenter.x + sourceCenter.w / 2;
      sourceCenter.min_y = sourceCenter.y - sourceCenter.h / 2 - 5;
      sourceCenter.max_y = sourceCenter.y + sourceCenter.h / 2 - 5;

      const targetD = this.axStates.find(el => el.guid === d.toStateGuid);
      const targetObj = document.getElementById(`d3_rect_${d.toStateGuid}`);
      // prettier-ignore
      const targetIsState = targetD.isStart === false
        && targetD.isDeleted === false
        && targetD.isAll === false;
      const targetCenter = {
        x: targetD.x,
        y: targetIsState
          ? targetD.y + d3.select(targetObj).attr('height') / 2
          : targetD.y,
        h: targetIsState ? d3.select(targetObj).attr('height') : 100,
        w: targetIsState ? d3.select(targetObj).attr('width') : 100,
        min_x: null,
        max_x: null,
        min_y: null,
        max_y: null
      };
      targetCenter.min_x = targetCenter.x - targetCenter.w / 2;
      targetCenter.max_x = targetCenter.x + targetCenter.w / 2;
      targetCenter.min_y = targetCenter.y - targetCenter.h / 2 - 5;
      targetCenter.max_y = targetCenter.y + targetCenter.h / 2 - 5;

      const sweetPoints = this.getCollisionPoints(sourceCenter, targetCenter);
      const straightLine = `M${sweetPoints.x1},${sweetPoints.y1} ${sweetPoints.x2},${sweetPoints.y2}`;
      let retLine = straightLine;

      if (d.radius !== 0) {
        const controlPoint = { x: null, y: null };

        // Находим точку на удалении mouseDistance
        const mouseDistance = d.radius;
        const targetSweetPoint = { x: sweetPoints.x2, y: sweetPoints.y2 };
        const calcDistance = this.getDistance(sourceCenter, targetSweetPoint);
        const ab05Distance = calcDistance / 2;
        const r0 = Math.sqrt(
          ab05Distance * ab05Distance + mouseDistance * mouseDistance
        );

        const mouseDistancePoints = this.intersect_two_circles(
          sourceCenter.x,
          sourceCenter.y,
          r0,
          targetSweetPoint.x,
          targetSweetPoint.y,
          r0
        );
        let mouseDistancePoint = {};
        if (d.radius > 0) {
          // right or left
          mouseDistancePoint = {
            x: mouseDistancePoints.x1,
            y: mouseDistancePoints.y1
          };
        } else {
          mouseDistancePoint = {
            x: mouseDistancePoints.x2,
            y: mouseDistancePoints.y2
          };
        }

        // P1=2P(0.5)−0.5P0−0.5P2
        // https://math.stackexchange.com/questions/1666026/find-the-control-point-of-quadratic-bezier-curve-having-only-the-end-points
        // prettier-ignore
        controlPoint.x = mouseDistancePoint.x * 2
          - sourceCenter.x / 2
          - targetSweetPoint.x / 2;
        // prettier-ignore
        controlPoint.y = mouseDistancePoint.y * 2
          - sourceCenter.y / 2
          - targetSweetPoint.y / 2;

        // drawDebugCircle("debug_controlPoint", "red", controlPoint.x, controlPoint.y);
        // eslint-disable-next-line max-len
        // drawDebugCircle("debug_mouse_distance_point", "green", mouse_distance_point.x, mouse_distance_point.y);

        // eslint-disable-next-line max-len
        // M50,50 Q50,100 100,100 == Curve from 50,50 to 100,100 with Quadratic Bezier Curve to point 50,100
        const curvedLine = `M${sourceCenter.x},${sourceCenter.y}Q${controlPoint.x},${controlPoint.y} ${sweetPoints.x2},${sweetPoints.y2}`;

        retLine = curvedLine;
      }

      return retLine;
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
    pointOnRect(x, y, minX, minY, maxX, maxY, validate) {
      // assert minX <= maxX;
      // assert minY <= maxY;
      if (validate && (minX < x && x < maxX) && (minY < y && y < maxY)) {
        // prettier-ignore
        const msg = `Point ${[x, y]}cannot be inside `
          + `the rectangle: ${[minX, minY]} - ${[maxX, maxY]}.`;
        this.$log.error(msg);
        return false;
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
      // if (x === midX && y === midY) console.log('ERROR');

      // Should never happen :) If it does, please tell me!
      // throw `Cannot find intersection for ${[x, y]} inside rectangle ${[
      //   minX,
      //   minY
      // ]} - ${[maxX, maxY]}.`;
      return false;
    },

    getCollisionPoints(source, target) {
      let sourceX;
      let targetX;
      let midX;

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
        targetX = midX;
        sourceX = midX;
      }

      const dx = targetX - sourceX;
      const dy = target.y - source.y;
      const angle = Math.atan2(dx, dy);

      return {
        x1: sourceX,
        y1: source.y + (Math.cos(angle) * source.h) / 2,
        x2: targetX,
        y2: target.y - (Math.cos(angle) * target.h) / 2
      };
    },

    checkStateName(name) {
      const isChecked = this.axStates.some(e => e.name === name);
      return isChecked;
    },
    checkActionName(name) {
      const isChecked = this.axActions.some(e => e.name === name);
      return isChecked;
    },

    async handleCreateState() {
      const globalG = document.getElementById('globalG');
      const coords = d3.mouse(globalG);

      const res = await this.$dialog.prompt({
        text: this.$t('workflow.state.add-state-prompt'),
        actions: {
          true: {
            text: this.$t('common.confirm')
          }
        }
      });
      if (res) {
        let nameIsChecked = false;
        let currentNum = 0;
        let currentName = res;

        while (nameIsChecked === false) {
          if (this.checkStateName(currentName)) {
            currentNum += 1;
            currentName = `${res} ${currentNum}`;
          } else nameIsChecked = true;
        }

        const args = {
          formGuid: this.$store.state.formGuid,
          name: currentName,
          x: coords[0],
          y: coords[1]
        };
        this.$store.dispatch('workflow/createState', args).then(() => {
          const msg = this.$t('workflow.state.add-state-toast');
          this.$dialog.message.success(
            `<i class="fas fa-project-diagram"></i> &nbsp ${msg}`
          );
        });
      }
    },

    async handleCreateAction(_fromStateGuid, _toStateGuid) {
      const res = await this.$dialog.prompt({
        text: this.$t('workflow.action.add-action-prompt'),
        actions: {
          true: {
            text: this.$t('common.confirm')
          }
        }
      });

      if (res) {
        const args = {
          formGuid: this.$store.state.formGuid,
          name: res,
          fromStateGuid: _fromStateGuid,
          toStateGuid: _toStateGuid
        };
        this.$store.dispatch('workflow/createAction', args).then(() => {
          const msg = this.$t('workflow.action.add-action-toast');
          this.$dialog.message.success(
            `<i class="fas fa-angle-double-right"></i> &nbsp ${msg}`
          );
        });
      }
    },

    handleEditState(d) {
      this.selectedStateGuid = d.guid;
      this.$modal.show('update-state');
    },

    updateModalState() {
      const stateGuid = this.$refs.stateModal.currentGuid;
      setTimeout(() => {
        d3.select(`#d3_state_g_${stateGuid}`).remove();
        this.redrawStates();
        this.closeModal();
      }, 100);
    },

    handleEditAction(d) {
      this.selectedActionGuid = d.guid;
      this.$modal.show('update-action');
    },

    updateModalAction() {
      const actionGuid = this.$refs.actionModal.currentGuid;
      setTimeout(() => {
        this.redrawSingleAction(actionGuid);
        this.closeModal();
      }, 100);
    },

    async handleStateDelete(guid) {
      this.name = this.$store.state.workflow.states.find(
        state => state.guid === guid
      ).name;

      const res = await this.$dialog.confirm({
        text: this.$t('workflow.state.state-delete-confirm', {
          name: this.name
        }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });

      if (res) {
        this.$store
          .dispatch('workflow/deleteState', {
            guid
          })
          .then(() => {
            const msg = this.$t('workflow.state.state-deleted-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            setTimeout(() => {
              d3.select(`#d3_state_g_${guid}`).remove();
              d3.selectAll('.d3_action_g').remove();
              this.redrawActions();
            }, 50);
          });
      }
    },

    async handleActionDelete(guid) {
      const actionToDelete = this.$store.state.workflow.actions.find(
        action => action.guid === guid
      );
      const actionName = actionToDelete.name;
      let isSelfActionState = null;
      if (actionToDelete.fromStateGuid === actionToDelete.toStateGuid) {
        isSelfActionState = actionToDelete.toStateGuid;
      }

      const res = await this.$dialog.confirm({
        text: this.$t('workflow.action.action-delete-confirm', {
          name: actionName
        }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });

      if (res) {
        this.$store
          .dispatch('workflow/deleteAction', {
            guid
          })
          .then(() => {
            const msg = this.$t('workflow.action.action-deleted-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            if (!isSelfActionState) d3.select(`#d3_action_g_${guid}`).remove();
            else {
              setTimeout(() => {
                this.redrawSingleState(isSelfActionState);
              }, 100);
            }
            // d3.select(`#d3_self_action_text_${guid}`).remove();
          });
      }
    },

    handleAddRoleToState(roleGuid, stateGuid) {
      // console.log(`Add ${roleGuid} role to ${stateGuid} state`);
      this.$store
        .dispatch('workflow/addRoleToState', {
          stateGuid,
          roleGuid
        })
        .then(() => {
          const roleName = this.$store.state.workflow.roles.find(
            element => element.guid === roleGuid
          ).name;
          const stateName = this.$store.state.workflow.states.find(
            element => element.guid === stateGuid
          ).name;

          const msg = this.$t('workflow.role.role-added-to-state-toast', {
            role: roleName,
            state: stateName
          });
          this.$dialog.message.success(
            `<i class="fas fa-user-plus"></i> &nbsp ${msg}`
          );
        });
    },

    handleAddRoleToAction(roleGuid, actionGuid) {
      // console.log(`Add ${roleGuid} role to ${stateGuid} action`);
      this.$store
        .dispatch('workflow/addRoleToAction', {
          actionGuid,
          roleGuid
        })
        .then(() => {
          const roleName = this.$store.state.workflow.roles.find(
            element => element.guid === roleGuid
          ).name;
          const actionName = this.$store.state.workflow.actions.find(
            element => element.guid === actionGuid
          ).name;

          const msg = this.$t('workflow.role.role-added-to-action-toast', {
            role: roleName,
            action: actionName
          });
          this.$dialog.message.success(
            `<i class="fas fa-user-plus"></i> &nbsp ${msg}`
          );
        });
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

    isLeft(lineFrom, lineTo, _point) {
      // if value > 0, p2 is on the left side of the line.
      // if value = 0, p2 is on the same line.
      // if value < 0, p2 is on the right side of the line.\
      // prettier-ignore
      const value = (lineTo.x - lineFrom.x) * (_point.y - lineFrom.y)
        - (_point.x - lineFrom.x) * (lineTo.y - lineFrom.y);
      if (value > 0) return true;
      return false;
    },

    getDistance(a, b) {
      const sideA = a.x - b.x;
      const sideB = a.y - b.y;
      return Math.sqrt(sideA * sideA + sideB * sideB);
    },

    getDistanceSquared(v, w) {
      return (v.x - w.x) * (v.x - w.x) + (v.y - w.y) * (v.y - w.y);
    },

    getCenterOfPath(_id) {
      const pathEl = d3.select(`#d3_action_${_id}`).node();
      const midpoint = pathEl.getPointAtLength(pathEl.getTotalLength() / 2);
      return midpoint;
    },

    getDistanceToLine(_point, lineStart, lineEnd) {
      const l2 = this.getDistanceSquared(lineStart, lineEnd);

      if (l2 === 0) {
        return Math.sqrt(this.getDistanceSquared(_point, lineStart));
      }
      // prettier-ignore
      const t = ((_point.x - lineStart.x) * (lineEnd.x - lineStart.x)
          + (_point.y - lineStart.y) * (lineEnd.y - lineStart.y))
        / l2;
      if (t < 0) {
        return Math.sqrt(this.getDistanceSquared(_point, lineStart));
      }
      if (t > 1) return Math.sqrt(this.getDistanceSquared(_point, lineEnd));

      const distanceSquared = this.getDistanceSquared(_point, {
        x: lineStart.x + t * (lineEnd.x - lineStart.x),
        y: lineStart.y + t * (lineEnd.y - lineStart.y)
      });
      return Math.sqrt(distanceSquared);
    },

    // drawDebugCircle(_id, _color, _x, _y) {
    //   d3.selectAll(`#${_id}`).remove();

    //   const circle = this.container
    //     .append('circle')
    //     .attr('id', _id)
    //     .attr('cx', _x)
    //     .attr('cy', _y)
    //     .attr('r', 5)
    //     .style('fill', _color);
    // },

    checkDelete(event) {
      if (event.keyCode === 46) {
        if (this.selectedStateId != null) {
          this.handleStateDelete(this.selectedStateId);
        }

        if (this.selectedActionId != null) {
          this.handleActionDelete(this.selectedActionId);
        }
      }
    },
    closeModal() {
      this.$modal.hide('update-state');
      this.$modal.hide('update-action');

      this.selectedStateGuid = null;
      this.selectedActionGuid = null;
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
#workflowContainer {
  width: 100%;
  height: 100%;
  background: #fff;
}
</style>
