#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "multimap.h"

#define NODE_LIST_START_SIZE   64
#define VALUE_LIST_START_SIZE  1

/*============================================================================
 * TYPES
 *
 *   These types are defined in the implementation file so that they can
 *   be kept hidden to code outside this source file.  This is not for any
 *   security reason, but rather just so we can enforce that our testing
 *   programs are generic and don't have any access to implementation details.
 *============================================================================*/


 /* Represents a the set of values that are associated with a given key. */
typedef struct value_list {
    int * list;
    int size;
    int max;
} value_list;


/* Represents a key and its associated values in the multimap, as well as
 * pointers to the left and right child nodes in the multimap. */
typedef struct multimap_node {
    /* A struct containing values associated with this key in the multimap. */
    struct value_list * values;
} multimap_node;


typedef struct node_list {
    multimap_node * list;
    int size;
} node_list;


/* The entry-point of the multimap data structure. */
struct multimap {
    struct node_list * nodes;
};


/*============================================================================
 * HELPER FUNCTION DECLARATIONS
 *
 *   Declarations of helper functions that are local to this module.  Again,
 *   these are not visible outside of this module.
 *============================================================================*/

multimap_node * find_mm_node(multimap * mm, int key,
                             int create_if_not_found);

void free_multimap_node(multimap_node *node);

value_list * new_value_list();
void add_to_value_list(value_list * vl, int value);
int remove_from_value_list(value_list * vl, int value);
int find_in_value_list(value_list * vl, int value);
void free_value_list(value_list * vl);

multimap_node new_mm_node();

node_list * new_node_list();
void add_to_node_list(node_list * nl, int key);
int remove_from_node_list(node_list * nl, int key);
multimap_node find_in_node_list(node_list * nl, int key);
void free_node_list(node_list * nl);

/*============================================================================
 * FUNCTION IMPLEMENTATIONS
 *============================================================================*/

/* Creates and returns new value_list. */
value_list * new_value_list() {
    struct value_list * vl = (value_list *) malloc(sizeof(struct value_list));

    /* Make sure alloc worked. */
    if (vl == NULL) {
        printf("error: unable to allocate memory for value_list.\n");
    }

    vl->size = 0;
    vl->max = VALUE_LIST_START_SIZE;
    vl->list = (int *) malloc(vl->max * sizeof(int));

    /* Make sure alloc worked. */
    if (vl->list == NULL) {
        printf("error: unable to allocate memory for value_list.\n");
    }

    return vl;
}

/* Adds value to value_list. Makes larger if needed. */
void add_to_value_list(value_list * vl, int value) {
    /* Check if resizing is needed. */
    if (vl->size + 1 > vl->max) {
        /* Make new size double. */
        vl->max *= 2;
        vl->list = (int *) realloc(vl->list, vl->max * sizeof(int));

        /* Make sure realloc worked. */
        if (vl->list == NULL) {
            printf("error: unable to reallocate memory for value_list.\n");
        }
    }

    /* Add new value to list. */
    vl->list[vl->size] = value;
    vl->size++;
}

/* Removes value from value_list. Makes smaller if needed. */
int remove_from_value_list(value_list * vl, int value) {
    /*Find value in list. */
    int i = 0, flag = 0;
    for (i = 0; i < vl->size; ++i) {
        if (vl->list[i] == value) {
            /* Remove by replacing with last value and decreasing size. */
            vl->list[i] = vl->list[vl->size - 1];
            vl->size--;
            flag = 1;
            break;
        }
    }

    /* If half of allocated memory, reallocate to use less memory. */
    if (vl->size <= (vl->max / 2)) {
        vl->max /= 2;
        vl->list = (int *) realloc(vl->list, vl->max * sizeof(int));

        /* Make sure realloc worked. */
        if (vl->list == NULL) {
            printf("error: unable to reallocate memory for value_list.\n");
        }
    }

    /* 1 if found the value, 0 otherwise. */
    return flag;
}

/* Returns 1 if value is in list, 0 otherwise. */
int find_in_value_list(value_list * vl, int value) {
    int i = 0;
    for (i = 0; i < vl->size; ++i) {
        if (vl->list[i] == value) {
            return 1;
        }
    }
    return 0;
}

/* Frees the value_list. */
void free_value_list(value_list * vl) {
    free(vl->list);
}

multimap_node new_mm_node() {
    multimap_node node;
    node.values = new_value_list();
    return node;
}

/* Creates and returns new node_list. */
node_list * new_node_list() {
    struct node_list * nl = (node_list *) malloc(sizeof(struct node_list));

    /* Make sure alloc worked. */
    if (nl == NULL) {
        printf("error: unable to allocate memory for node_list.\n");
    }

    nl->size = NODE_LIST_START_SIZE;
    nl->list =
        (multimap_node *) malloc(nl->size * sizeof(struct multimap_node));

    /* Make sure alloc worked. */
    if (nl->list == NULL) {
        printf("error: unable to allocate memory for node_list.\n");
    }

    /* Populate memory region with empty nodes. */
    int i;
    for (i = 0; i < nl->size; ++i) {
        nl->list[i] = new_mm_node();
    }

    return nl;
}

void add_to_node_list(node_list * nl, int key) {
    /* Check if reallocation is needed. */
    if (key >= nl->size) {
        int prev_size = nl->size, i;
        nl->size *= ceil(key / prev_size) + 1;
        nl->list = (multimap_node *)
            realloc(nl->list, nl->size * sizeof(struct multimap_node));

        /* Make sure realloc worked. */
        if (nl->list == NULL) {
            printf("error: unable to reallocate memory for node_list.\n");
        }

        /* Populate new memory region with empty nodes. */
        for (i = prev_size; i < nl->size; ++i) {
            nl->list[i] = new_mm_node();
        }
    }
}

int remove_from_node_list(node_list * nl, int key) {
    /* Check if key is in node list. */
    if (key < nl->size) {
        /* Free the list, create a new one. */
        free(nl->list[key].values);
        nl->list[key].values = new_value_list();
        return 1;
    }

    /* Return 0 if it is not. */
    return 0;
}

multimap_node find_in_node_list(node_list * nl, int key) {
    assert(key < nl->size);
    return nl->list[key];
}

void free_node_list(node_list * nl) {
    free(nl);
}

/* This helper function searches for the multimap node that contains the
 * specified key.  If such a node doesn't exist, the function can initialize
 * a new node and add this into the structure, or it will simply return NULL.
 * The one exception is the root - if the root is NULL then the function will
 * return a new root node.
 */
multimap_node * find_mm_node(multimap * mm, int key,
                             int create_if_not_found) {

    /* If key does not exist and not creating, return NULL. */
    if (key >= mm->nodes->size && !create_if_not_found) {
        return NULL;
    }

    /* If key does not exist and creating, create new node and return. */
    if (key >= mm->nodes->size) {
        add_to_node_list(mm->nodes, key);
    }

    /* If it got here key does exist, so return node. */
    return &mm->nodes->list[key];
}


/* This helper function frees a multimap node, including its children and
 * value-list.
 */
void free_multimap_node(multimap_node *node) {
    if (node == NULL)
        return;

    /* Free the list of values. */
    free_value_list(node->values);

    /* Free node itself. */
    free(node);
}


/* Initialize a multimap data structure. */
multimap * init_multimap() {
    multimap *mm = malloc(sizeof(multimap));

    /* Allocates a node_list for the new multimap. */
    mm->nodes = new_node_list();

    return mm;
}


/* Release all dynamically allocated memory associated with the multimap
 * data structure.
 */
void clear_multimap(multimap *mm) {
    assert(mm != NULL);

    /* Free the node list. */
    free_node_list(mm->nodes);
}


/* Adds the specified (key, value) pair to the multimap. */
void mm_add_value(multimap *mm, int key, int value) {
    /* Find key's node, if it does not exist then create. */
    multimap_node * node = find_mm_node(mm, key, /* create */ 1);

    /* Add the value to the nodes list. */
    add_to_value_list(node->values, value);
}


/* Returns nonzero if the multimap contains the specified key-value, zero
 * otherwise.
 */
int mm_contains_key(multimap *mm, int key) {
    multimap_node *node;

    node = find_mm_node(mm, key, /* create */ 0);

    if (node->values->size == 0) {
        return 0;
    }
    return 1;
}


/* Returns nonzero if the multimap contains the specified (key, value) pair,
 * zero otherwise.
 */
int mm_contains_pair(multimap *mm, int key, int value) {
    multimap_node *node;

    node = find_mm_node(mm, key, /* create */ 0);
    if (node == NULL)
        return 0;

    return find_in_value_list(node->values, value);
}


/* Removes the specified (key, value) pair from the multimap.  Returns 1 if
 * the specified pair was found, or 0 if the pair was not found.
 */
int mm_remove_pair(multimap *mm, int key, int value) {
    multimap_node *node;

    assert(mm != NULL);

    /* Find key's node, if it does not exist then do not create. */
    node = find_mm_node(mm, key, /* create */ 0);

    /* If key does not exist then obviously pair does not exist. */
    if (node == NULL)
        return 0;

    /* Remove the value from the node's list and return whether or not found. */
    return remove_from_value_list(node->values, value);
}


/* Performs an in-order traversal of the multimap, passing each (key, value)
 * pair to the specified function.
 */
void mm_traverse(multimap *mm, void (*f)(int key, int value)) {
    int i, j;
    for (i = 0; i < mm->nodes->size; ++i) {
        for (j = 0; j < mm->nodes->list[i].values->size; ++j) {
            (*f) (i, mm->nodes->list[i].values->list[j]);
        }
    }
}

